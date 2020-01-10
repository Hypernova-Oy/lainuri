from lainuri.config import get_config
from lainuri.logging_context import logging
log = logging.getLogger(__name__)

from simple_websocket_server import WebSocket
import json

import lainuri.websocket_server

class LEvent():
  serializable_attributes = [] # Must be overloaded

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
    if not self.message:
      msg = {}
      for att in self.serializable_attributes:
        msg[att] = getattr(self, att)
      self.message = msg

    return json.dumps({
      'event': self.event,
      'message': self.message,
      'event_id': self.event_id,
    })

  def validate_params(self):
    for attribute_name in self.serializable_attributes:
      if not(getattr(self, attribute_name) or getattr(self, attribute_name) == 0):
        self.throw_missing_attribute(attribute_name)

  def throw_missing_attribute(self, attribute_name: str):
    class_name = type(self)
    raise Exception(f"{class_name}():> Missing attribute '{attribute_name}'")


class LEBarcodeRead(LEvent):
  event = 'barcode-read'

  serializable_attributes = ['barcode']
  barcode = ''

  def __init__(self, barcode: str, client: WebSocket = None, recipient: WebSocket = None, event_id: str = None):
    self.barcode = barcode
    super().__init__(event=self.event, client=client, recipient=recipient, event_id=event_id)
    self.validate_params()

class LERFIDTagsLost(LEvent):
  event = 'rfid-tags-lost'

  serializable_attributes = ['tags_lost','tags_present']
  tags_present = []

  def __init__(self, tags_lost: list, tags_present: list, client: WebSocket = None, recipient: WebSocket = None, event_id: str = None):
    self.tags_present = tags_present
    self.tags_lost = tags_lost
    message = {
      'tags_lost': [tag.serial_number() for tag in self.tags_lost],
      'tags_present': [tag.serial_number() for tag in self.tags_present],
    }
    super().__init__(event=self.event, message=message, client=client, recipient=recipient, event_id=event_id)
    self.validate_params()

class LERFIDTagsNew(LEvent):
  event = 'rfid-tags-new'

  serializable_attributes = ['tags_new','tags_present']
  tags_present = []

  def __init__(self, tags_new: list, tags_present: list, client: WebSocket = None, recipient: WebSocket = None, event_id: str = None):
    self.tags_present = tags_present
    self.tags_new = tags_new
    message = {
      'tags_new': [tag.serial_number() for tag in self.tags_new],
      'tags_present': [tag.serial_number() for tag in self.tags_present],
    }
    super().__init__(event=self.event, message=message, client=client, recipient=recipient, event_id=event_id)
    self.validate_params()

class LERFIDTagsPresent(LEvent):
  event = 'rfid-tags-present'

  serializable_attributes = ['tags_present']
  tags_present = []

  def __init__(self, tags_present: list, client: WebSocket = None, recipient: WebSocket = None, event_id: str = None):
    self.tags_present = tags_present
    message = {
      'tags_present': [tag.serial_number() for tag in tags_present],
    }
    super().__init__(event=self.event, message=message, client=client, recipient=recipient, event_id=event_id)
    self.validate_params()
