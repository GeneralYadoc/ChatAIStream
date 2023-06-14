# ChatAIStream
Message broker between YouTube chat stream and ChatGPT.

## The user of this library can
- pick up massegase from YouTube Chat and generate answer by ChatGPT.
- easily give role to ChatGPT.

## How to install

### Install from PyPI
- Install package to your environment.<br>
    ```install
    $ pip install chatai-stream
    ```

### Install from GitHub repository
- Clone this repository.<br>
  ```clone
  $ clone https://github.com/GeneralYadoc/ChatAIStream.git
  ```
- Change directory to the root of the repository.<br>
  ```cd
  $ cd ChatAIStream
  ```
- Install package to your environment.<br>
  ```install
  $ pip install .
  ```
## How to use
- [OpenAI API Key](https://www.howtogeek.com/885918/how-to-get-an-openai-api-key/) is necessary to execute following sample.

- Sample codes exist [here](samples/sample.py).
  ``` sample.py
  import sys
  import time
  import math
  import datetime
  import ChatAIStream as cas

  # print sentence by a character incrementally.
  def print_incremental(st, interval_sec):
    for i in range(len(st)):
      if not running:
        break
      print(f"{st[i]}", end='')
      sys.stdout.flush()
      interruptible_sleep(interval_sec)

  # Customized sleep for making available of running flag interruption.
  def interruptible_sleep(time_sec):
    counter = math.floor(time_sec / 0.10)
    frac = time_sec - (counter * 0.10)
    for i in range(counter):
      if not running:
        break
      time.sleep(0.10)
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

  # Turn off runnging flag in order to finish printing messages and answers by the sample.
  running=False

  # Finish getting ChatGPT answers.
  # Internal thread will stop soon.
  ai_stream.disconnect()

  # terminating internal thread.
  ai_stream.join()

  del ai_stream

  ```

- Usage of the sample
  ```usage
  $ python3 ./sample.py VIDEO-ID OpenAI-API-KEY
  ```
- Output of the sample<br>
  The outputs of the right window are provided by this sample.<br>
  Left outputs are also available by ChatAIStream.
  ![](ReadMeParts/ChatAIAgent.gif)

## Arguments of Constructor
- ChatAIStream object can be configured with following params given to constructor.

  ### streamParams
    | name | description | default |
    |------|------------|---------|
    | video_id | String following after 'v=' in url of target YouTube live | - |
    | get_item_cb | Chat items are thrown to this callback | None |
    | pre_filter_cb | Filter set before internal queue | None |
    | post_filter_cb | Filter set between internal queue and get_item_cb | None |
    | max_queue_size | Max slots of internal queue (0 is no limit) | 1000 |
    | interval_sec | Polling interval of picking up items from YouTube | 0.01 \[sec\] | 
  ### aiParams


    | name | description | default |
    |------|------------|---------|
    | api_key | API Key string of OpenAI | - |
    | system_role | ChatGPT role in convesation | "You are a helpful assistant." |
    | ask_cb | user message given to ChatGPT is thrown to this callback | None |
    | max_messages_in_context | Max messages in context given to ChatGPT | 20 |
    | answer_cb | ChatGPT answer is thrown to this callback | None |
    | max_queue_size | Max slots of internal queue (0 is no limit) | 10 |
    | model | Model of AI to be used. | None |
    | max_tokens_per_request | Max number of tokens which can be contained in a request. | 256 |
    | interval_sec | Interval of ChatGPT API call | 20.0 \[sec\] | 
### Notice
- Please refer [pytchat README](https://github.com/taizan-hokuto/pytchat) to know the type of YouTube Chat item used by get_item_cb, pre_filter_cb and post filter_cb.
- Emoticons in a message and messages consisted by emoticons only are removed defaultly even if user doesn't set pre_filter_cb.
- Default value of interval_sec is 20.0, since free user of OpenAI API can get only 3 completions per minitue.
- The system role given by user remains ever as the oldest sentence of current context even if the number of messages is reached to the maximum, so ChatGPT doesn't forgot the role while current cunversation.

## Methods
### start()
- Start YouTube Chat polling and ChatGPT conversation, then start calling user callbacks asyncronously.
- No arguments required, nothing returns.

### join()
- Wait terminating internal threads kicked by start().
- No arguments required, nothing returns.

### connect()
- Start YouTube Chat polling and ChatGPT conversation, then start calling user callbacks syncronously.
- Lines following the call of the method never executen before terminate of internal threads.
- No arguments required, nothing returns.

### disconnect()
- Request to terminate YouTube Chat polling, ChatGPT conversation and calling user callbacks.
- Internal process will be terminated soon after.
- No arguments required, nothing returns.

### full_messages_for_ask()
- Indicate whether the queue which spools messages to send ChatAI is full or not.

And other [threading.Thread](https://docs.python.org/3/library/threading.html) public pethods are available.

## Callbacks
### get_item_cb
- Callback for getting YouTube chat items.
- You can implement several processes in it.
- YouTube chat item is thrown as an argument.
- It's not be assumed that any values are returned.
### pre_filter_cb
- pre putting queue filter.
- YouTube chat item is thrown as an argument.
- You can edit YouTube chat items before putting internal queue.
- <b>If you want to get Complete items from YouTube, please implement this callback, since emoticons in a message and messages consisted by emoticons only are already removed from the items gotten in get_item_cb.</b> 
- It's required that edited chat item is returned.
- You can avoid putting internal queue by returning None.
### post_filter_cb
- post getting queue filter
- You can edit YouTube chat items after popping internal queue.
- It's required that edited chat item is returned.
- You can avoid sending item to get_item_cb by returning None.
### ask_cb
- Callback for getting questions that actually thrown to ChatGPT.
- If you register external info to user message when you put it, you can obtain the external info here.
- It's not be assumed that any values are returned.
### answer_cb
- Callback for getting question and answer of ChatGPT
- The type of completion is mentioned [here](https://platform.openai.com/docs/guides/chat).
- It's not be assumed that any values are returned.

## Links
ChatAIStream uses following libraries internally.

- [streamchat-agent](https://github.com/GeneralYadoc/StreamChatAgent)<br>
 YouTube chat poller which can get massages very smothly by using internal queue.
- [chatai-agent](https://github.com/GeneralYadoc/ChatAIAgent)<br>
 Message broker between user and ChatGPT.
