from simple_websocket_server import WebSocket
import json

class LEvent():
  def __init__(self, event: str = None, message: dict = None, client: WebSocket = None, recipient: WebSocket = None):
    self.event = event
    self.message = message
    self.client = client
    self.recipient = recipient

  def from_ws(self, client: WebSocket):
    self.message = json.loads(client.data)
    self.event = self.message['event']
    self.client = client
    return self

class LEventException(LEvent):
  def __init__(self, event: str, message: dict, e: Exception):
    self.event = event
    self.message = message
    self.e = e
