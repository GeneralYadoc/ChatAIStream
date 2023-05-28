# To execute this sample, please install streamchat-agent from PyPI as follows.
# $ pip install streamchat-agent
import sys
import time
import math
import datetime
import ChatAIStream as cas

# print sentencce by a character incrementally.
def print_incremental(st, interval_sec):
  for i in range(len(st)):
    if not running:
      break
    print(f"{st[i]}", end='')
    sys.stdout.flush()
    interruptible_sleep(interval_sec)

# Customized sleep for making available of running flag interruption.
def interruptible_sleep(time_sec):
  counter = math.floor(time_sec / 0.01)
  frac = time_sec - (counter * 0.01)
  for i in range(counter):
    if not running:
      break
    time.sleep(0.01)
  if not running:
    return
  time.sleep(frac)

# callback for getting answer of ChatGPT
def answer_cb(user_message, completion):
  print(f"\n[{user_message.extern.author.name} {user_message.extern.datetime}] {user_message.message}\n")
  interruptible_sleep(3)
  time_str = datetime.datetime.now().strftime ('%H:%M:%S')
  message = completion.choices[0]["message"]["content"]
  print(f"[ChatGPT {time_str}] ", end='')
  print_incremental(message, 0.05)
  print("\n")
  interruptible_sleep(5)

running = False

# YouTube Video ID and ChatGPT API Key is given from command line in this example.
if len(sys.argv) <= 2:
  exit(0)

# Set params of getting messages from stream source.
stream_params=cas.streamParams(video_id=sys.argv[1])

# Set params of Chat AI.
ai_params=cas.aiParams(
  api_key = sys.argv[2],
  system_role = "You are a cheerful assistant who speek English and can get conversation exciting with user.",
  answer_cb = answer_cb
)

# Create ChatAIStream instance.
ai_stream = cas.ChatAIStream(cas.params(stream_params=stream_params, ai_params=ai_params))

running = True

# Wake up internal thread to get chat messages from stream and ChatGPT answers.
ai_stream.start()

# Wait any key inputted from keyboad.
input()

# Turn off runnging flag in order to finish printing fung of dhit sample.
running=False

# Finish getting ChatGPT answers.
# Internal thread will stop soon.
ai_stream.disconnect()

# terminating internal thread.
ai_stream.join()

del ai_stream
