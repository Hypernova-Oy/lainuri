from lainuri.config import get_config
from lainuri.logging_context import logging
log = logging.getLogger(__name__)

from simple_websocket_server import WebSocket
import json
import traceback

import lainuri.websocket_handlers.ringtone
import lainuri.websocket_handlers.test
import lainuri.websocket_handlers.config
import lainuri.websocket_handlers.checkout
import lainuri.koha_api as koha_api

event_id: int = 0
def get_event_id(event_name: str) -> str:
  global event_id
  event_id += 1
  return event_name + '-' + str(event_id)

class LEvent():
  serializable_attributes = [] # Must be overloaded
  default_handler = None

  def __init__(self, event: str = None, message: dict = None, client: WebSocket = None, recipient: WebSocket = None, event_id: str = None):
    self.event = event
    self.message = message
    self.client = client
    self.recipient = recipient
    self.event_id = event_id
    if not(self.event_id) and self.event: self.event_id = get_event_id(self.event)

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

class LECheckOuting(LEvent):
  event = 'check-outing'
  default_handler = lainuri.websocket_handlers.checkout.checkout

  serializable_attributes = ['item_barcode', 'user_barcode']
  item_barcode = ''
  user_barcode = 0

  def __init__(self, item_barcode: str, user_barcode: str, client: WebSocket = None, recipient: WebSocket = None, event_id: str = None):
    self.item_barcode = item_barcode
    self.user_barcode = user_barcode
    super().__init__(event=self.event, client=client, recipient=recipient, event_id=event_id)
    self.validate_params()

class LECheckOuted(LEvent):
  event = 'check-outed'

  serializable_attributes = ['item_barcode', 'user_barcode', 'statuses']
  item_barcode = ''
  user_barcode = 0
  statuses = {}

  def __init__(self, item_barcode: str, user_barcode: str, statuses: dict, client: WebSocket = None, recipient: WebSocket = None, event_id: str = None):
    self.item_barcode = item_barcode
    self.user_barcode = user_barcode
    self.statuses = statuses
    super().__init__(event=self.event, client=client, recipient=recipient, event_id=event_id)
    self.validate_params()

class LECheckOutFailed(LEvent):
  event = 'check-out-failed'

  serializable_attributes = ['item_barcode', 'user_barcode', 'statuses']
  item_barcode = ''
  user_barcode = 0
  statuses = {}

  def __init__(self, item_barcode: str, user_barcode: str, statuses: dict, client: WebSocket = None, recipient: WebSocket = None, event_id: str = None):
    self.item_barcode = item_barcode
    self.user_barcode = user_barcode
    self.statuses = statuses
    super().__init__(event=self.event, client=client, recipient=recipient, event_id=event_id)
    self.validate_params()

class LERingtonePlay(LEvent):
  event = 'ringtone-play'
  default_handler = lainuri.websocket_handlers.ringtone.ringtone_play

  serializable_attributes = ['ringtone_type', 'ringtone']
  ringtone_type = ''
  ringtone = ''

  def __init__(self, ringtone_type: str = None, ringtone: str = None, client: WebSocket = None, recipient: WebSocket = None, event_id: str = None):
    self.ringtone_type = ringtone_type
    self.ringtone = ringtone
    message = {key: getattr(self, key) for key in self.serializable_attributes}
    super().__init__(event=self.event, message=message, client=client, recipient=recipient, event_id=event_id)

class LERingtonePlayed(LEvent):
  event = 'ringtone-played'

  serializable_attributes = ['ringtone_type', 'ringtone']
  ringtone_type = ''
  ringtone = ''

  def __init__(self, ringtone_type: str = None, ringtone: str = None, client: WebSocket = None, recipient: WebSocket = None, event_id: str = None):
    self.ringtone_type = ringtone_type
    self.ringtone = ringtone
    message = {key: getattr(self, key) for key in self.serializable_attributes}
    super().__init__(event=self.event, message=message, client=client, recipient=recipient, event_id=event_id)

class LEBarcodeRead(LEvent):
  event = 'barcode-read'

  serializable_attributes = ['barcode']
  barcode = ''

  def __init__(self, barcode: str, client: WebSocket = None, recipient: WebSocket = None, event_id: str = None):
    self.barcode = barcode
    super().__init__(event=self.event, client=client, recipient=recipient, event_id=event_id)
    self.validate_params()

class LEConfigWrite(LEvent):
  event = 'config-write'
  default_handler = lainuri.websocket_handlers.config.write_config

  serializable_attributes = ['variable', 'new_value']
  variable = ''
  new_value = ''

  def __init__(self, variable: str, new_value: str, client: WebSocket = None, recipient: WebSocket = None, event_id: str = None):
    self.variable = variable
    self.new_value = new_value
    message = {key: getattr(self, key) for key in self.serializable_attributes}
    super().__init__(event=self.event, message=message, client=client, recipient=recipient, event_id=event_id)
    self.validate_params()

class LERFIDTagsLost(LEvent):
  event = 'rfid-tags-lost'

  serializable_attributes = ['tags_lost','tags_present']
  tags_present = []

  def __init__(self, tags_lost: list, tags_present: list, client: WebSocket = None, recipient: WebSocket = None, event_id: str = None):
    self.tags_present = tags_present
    self.tags_lost = tags_lost
    message = {
      'tags_lost': [koha_api.get_fleshed_item_record(tag.serial_number()) for tag in self.tags_lost],
      'tags_present': [koha_api.get_fleshed_item_record(tag.serial_number()) for tag in self.tags_present],
    }
    super().__init__(event=self.event, message=message, client=client, recipient=recipient, event_id=event_id)

class LERFIDTagsNew(LEvent):
  event = 'rfid-tags-new'

  serializable_attributes = ['tags_new','tags_present']
  tags_present = []

  def __init__(self, tags_new: list, tags_present: list, client: WebSocket = None, recipient: WebSocket = None, event_id: str = None):
    self.tags_present = tags_present
    self.tags_new = tags_new
    message = {
      'tags_new': [koha_api.get_fleshed_item_record(tag.serial_number()) for tag in self.tags_new],
      'tags_present': [koha_api.get_fleshed_item_record(tag.serial_number()) for tag in self.tags_present],
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
      'tags_present': [koha_api.get_fleshed_item_record(tag.serial_number()) for tag in tags_present],
    }
    super().__init__(event=self.event, message=message, client=client, recipient=recipient, event_id=event_id)
    self.validate_params()

class LEUserLoggingIn(LEvent):
  event = 'user-logging-in'

  serializable_attributes = ['username', 'password']
  username = ''
  password = ''

  lifecycle_map_event_to_hooks = {
    'LEUserLoggedIn': 'onsuccess',
    'LEException': 'onerror',
  }

  def __init__(self, username: str = None, password:str = None, client: WebSocket = None, recipient: WebSocket = None, event_id: str = None):
    self.password = password
    message = {key: getattr(self, key) for key in self.serializable_attributes}
    super().__init__(event=self.event, message=message, client=client, recipient=recipient, event_id=event_id)
    #self.validate_params()

class LEUserLoggedIn(LEvent):
  event = 'user-logged-in'

  serializable_attributes = ['firstname', 'surname', 'user_barcode']
  firstname = ''
  surname = ''
  user_barcode = ''

  lifecycle_map_event_to_hooks = {
    'LEUserLoggedIn': 'onsuccess',
    'LEException': 'onerror',
  }

  def __init__(self, firstname: str, surname: str, user_barcode: str, client: WebSocket = None, recipient: WebSocket = None, event_id: str = None):
    self.firstname = firstname
    self.surname = surname
    self.user_barcode = user_barcode
    message = {key: getattr(self, key) for key in self.serializable_attributes}
    super().__init__(event=self.event, message=message, client=client, recipient=recipient, event_id=event_id)
    self.validate_params()

class LEUserLoginAbort(LEvent):
  event = 'user-login-abort'

  def __init__(self, client: WebSocket = None, recipient: WebSocket = None, event_id: str = None):
    super().__init__(event=self.event, message=None, client=client, recipient=recipient, event_id=event_id)

class LERegisterClient(LEvent):
  event = 'register-client'

  def __init__(self, client: WebSocket = None, recipient: WebSocket = None, event_id: str = None):
    super().__init__(event=self.event, message=None, client=client, recipient=recipient, event_id=event_id)

class LEDeregisterClient(LEvent):
  event = 'deregister-client'

  def __init__(self, client: WebSocket = None, recipient: WebSocket = None, event_id: str = None):
    super().__init__(event=self.event, message=None, client=client, recipient=recipient, event_id=event_id)
class LETestMockDevices(LEvent):
  event = 'test-mock-devices'
  default_handler = lainuri.websocket_handlers.test.mock_devices

  def __init__(self, client: WebSocket = None, recipient: WebSocket = None, event_id: str = None):
    super().__init__(event=self.event, message=None, client=client, recipient=recipient, event_id=event_id)

class LEException(LEvent):
  event = 'exception'

  serializable_attributes = ['exception']
  exception = ''
  e = Exception()

  def __init__(self, e, client: WebSocket = None, recipient: WebSocket = None, event_id: str = None):
    if isinstance(e, Exception):
      self.e = e
      self.exception = traceback.format_exc()
    else:
      self.exception = e

    message = {
      'exception': self.exception,
    }
    super().__init__(event=self.event, message=message, client=client, recipient=recipient, event_id=event_id)
    self.validate_params()

class LEUserLoginFailed(LEException):
  event = 'user-login-failed'
