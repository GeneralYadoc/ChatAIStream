# ChatAIAgent
Message broker between user and ChatGPT.

## The user of this library can
- easily give role and messages to ChatGPT, and obtain answers.
- spool messages which given before ChatGPT finish generating current answer.

## Hou to install

### Install from PyPI
- Install package to your environment.<br>
    ```install
    $ pip install chatai-agent
    ```

### Install from GitHub repository
- Clone this repository.<br>
  ```clone
  $ clone https://github.com/GeneralYadoc/ChatAIAgent.git
  ```
- Change directory to the root of the repository.<br>
  ```cd
  $ cd ChatAIAgent
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
  import datetime
  import ChatAIAgent as ca  # Import this.

  # callback for getting questions that actually thrown to ChatGPT
  # If you register external info to user message when you put it, you can obtain the external info here.
  def ask_cb(user_message):
    time_str = user_message.extern.strftime ('%H:%M:%S')
    print(f"\n[question {time_str}] {user_message.message}\n")

  # callback for getting answer of ChatGPT
  def answer_cb(user_message, completion):
    time_str = datetime.datetime.now().strftime ('%H:%M:%S')
    message = completion.choices[0]["message"]["content"]
    print(f"[answer {time_str}] {message}\n")

  # ChatGPT API Key is given from command line in this example.
  if len(sys.argv) <= 1:
    exit(0)

  system_role="You are a cheerful assistant who speek English and can get conversation exciting with user."

  # Create ChatAIAgent instance.
  params = ca.params(
    api_key=sys.argv[1],
    system_role=system_role,
    ask_cb=ask_cb,
    answer_cb=answer_cb,
    max_tokens_per_request = 2048
  )
  agent = ca.ChatAIAgent( params )

  # Wake up internal thread on which ChatGPT answer messages will be generated.
  agent.start()

  while True:
    message = input("")
    if message == "":
      break
    # Put message received from stdin on internal queue to be available from internal thread.
    agent.put_message(ca.userMessage(message=message,extern=datetime.datetime.now()))

  # Finish generating answers.
  # Internal thread will stop soon.
  agent.disconnect()

  # terminating internal thread.
  agent.join()

  del agent
  ```

- Output of the sample
  ```output
  $ python3 samples/sample.py XXXXXXXXXXXXXXXXXX (OpenAI API Key) 
  Who are you?

  [question 17:30:35] Who are you?

  [answer 17:30:37] Hello! I am a cheerful assistant and I'm here to help you. My name is not important, but I'm happy to assist you with anything you need. How can I help you today?

  Would you make sound of a cat?

  [question 17:31:14] Would you make sound of a cat?

  [answer 17:31:16] Meow! Meow! That's the sound a cat makes. Is there anything else you would like me to assist you with?
    ```
## Arguments of Constructor
- ChatAIAgent object can be configured with following params given to constructor.

    | name | description | default |
    |------|------------|---------|
    | api_key | API Key string of OpenAI | - |
    | system_role | API Key string of OpenAI | - |
    | ask_cb | user message given to ChatGPT is thrown to this callback | None |
    | max_messages_in_context | Max messages in context given to ChatGPT | 20 |
    | answer_cb | ChatGPT answer is thrown to this callback | None |
    | max_queue_size | Max slots of internal queue (0 is no limit) | 10 |
    | model | Model of AI to be used. | None |
    | max_tokens_per_request | Max number of tokens which can be contained in a request. | 256 |
    | interval_sec | Interval of ChatGPT API call | 20.0 \[sec\] | 
### Notice
- Default value of interval_sec is 20.0, since free user of OpenAI API can get only 3 completions per minitue.

## Methods
### start()
- Start ChatGPT conversation and calling user callbacks asyncronously.
- No arguments required, nothing returns.

### join()
- Wait terminating internal threads kicked by start().
- No arguments required, nothing returns.

### connect()
- Start ChatGPT conversation and calling user callbacks syncronously.
- Lines following the call of the method never executen before terminate of internal threads.
- No arguments required, nothing returns.

### disconnect()
- Request to terminate conversation and calling user callbacks.
- Internal process will be terminated soon after.
- No arguments required, nothing returns.

And other [threading.Thread](https://docs.python.org/3/library/threading.html) public pethods are available.

## Callbacks
### ask_cb
- Callback for getting questions that actually thrown to ChatGPT.
- If you register external info to user message when you put it, you can obtain the external info here.
- It's not be assumed that any values are returned.
### answer_cb
- Callback for getting question and answer of ChatGPT
- The type of completion is mentioned [here](https://platform.openai.com/docs/guides/chat).
- It's not be assumed that any values are returned.

## Concept of design
- User message is put on internal queue and treated on internal thread.<br>
This feature gives advantage when You put ChatGPT on chat stream.<br>
Please try [this sample](samples/sample2.py) to experience the benefit.
  ```usage
  $ python3 ./sample2.py VIDEO-ID OpenAI-API-KEY
  ```
  ![](ReadMeParts/ChatAIAgent.gif)
- The system role given by user remains ever as the oldest sentence of current context even if the number of messages is reached to the maximum, so ChatGPT doesn't forgot the role while current cunversation.

## Links
StreamingChaatAgent uses following libraries internally.

- [streamchat-agent](https://github.com/GeneralYadoc/StreamChatAgent)<br> YouTube chat poller which can get massages very smothly by using internal queue.
