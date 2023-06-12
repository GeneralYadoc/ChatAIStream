import re
import threading
from typing import Callable
from dataclasses import dataclass
import StreamChatAgent as sca
import ChatAIAgent as ca

streamParams = sca.params
userMessage = ca.userMessage
aiParams = ca.params

@dataclass
class params():
  stream_params: streamParams
  ai_params: aiParams

class ChatAIStream(threading.Thread):
  def __my_pre_filter_cb(self, c):
    prefiltered_c = c
    if prefiltered_c and self.pre_filter_cb:
      prefiltered_c = self.pre_filter_cb(prefiltered_c)
    prefiltered_c.message = re.sub(r':[^:]+:', ".", prefiltered_c.message)
    prefiltered_c.message = re.sub(r'^[\.]+', "", prefiltered_c.message)
    return None if prefiltered_c.message == "" else prefiltered_c

  def __ask_stream_message_to_ai(self, c):
    if self.get_stream_message_cb:
      self.get_stream_message_cb(c)
    if self.ai_agent:
      self.ai_agent.put_message(ca.userMessage(message=c.message, extern=c))
  
  def __init__( self, params):
    self.get_stream_message_cb=params.stream_params.get_item_cb
    params.stream_params.get_item_cb=self.__ask_stream_message_to_ai
    self.pre_filter_cb=params.stream_params.pre_filter_cb
    params.stream_params.pre_filter_cb=self.__my_pre_filter_cb

    self.ai_agent = ca.ChatAIAgent( params.ai_params )
    self.stream_agent = sca.StreamChatAgent( params.stream_params )
    
    super(ChatAIStream, self).__init__(daemon=True)
  
  def full_messages_for_ask(self):
    return self.ai_agent.full_messages()

  def run(self):
    self.stream_agent.start()
    self.ai_agent.start()

  def connect(self):
    self.start()
    self.join()

  def disconnect(self):
    self.ai_agent.disconnect()
    self.stream_agent.disconnect()

