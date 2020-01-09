from simple_websocket_server import WebSocket
import json

import lainuri.websocket_server

class LEvent():
  def __init__(self, event: str = None, message: dict = None, client: WebSocket = None, recipient: WebSocket = None, event_id: str = None):
    self.event = event
    self.message = message
    self.client = client
    self.recipient = recipient
    self.event_id = event_id
    if not(self.event_id) and self.event: self.event_id = lainuri.websocket_server.get_event_id(self.event)

  def from_ws(self, client: WebSocket):
    payload = json.loads(client.data)
    self.message = payload['message']
    self.event = payload['event']
    self.client = client
    self.event_id = payload['event_id']
    if not self.event_id: raise Exception(f"Event '{self.event}' is missing event_id!")
    return self

  def serialize_ws(self):
    return json.dumps({
      'event': self.event,
      'message': self.message,
      'event_id': self.event_id,
    })
