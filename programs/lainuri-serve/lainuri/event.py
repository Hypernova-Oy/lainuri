from lainuri.config import get_config
from lainuri.logging_context import logging
log = logging.getLogger(__name__)

from simple_websocket_server import WebSocket
import json
import time
import traceback

from lainuri.constants import Status
import lainuri.koha_api as koha_api

event_id: int = 0
def get_event_id(event_name: str) -> str:
  global event_id
  event_id += 1
  return event_name + '-' + str(event_id)

class LEvent():
  serializable_attributes = [] # Must be overloaded
  default_handler = None
  default_recipient = None

  def __init__(self, event: str = None, message: dict = None, client: WebSocket = None, recipient: WebSocket = None, event_id: str = None):
    self.event = event
    self.message = message
    self.client = client
    self.recipient = recipient
    self.event_id = event_id
    self.timestamp = time.strftime("%H:%M:%S", time.localtime())
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
      if not(hasattr(self, attribute_name)):
        self.throw_missing_attribute(attribute_name)

  def throw_missing_attribute(self, attribute_name: str):
    class_name = type(self)
    raise Exception(f"{class_name}():> Missing attribute '{attribute_name}'")

class LECheckOut(LEvent):
  event = 'check-out'
  default_handler = 'lainuri.websocket_handlers.checkout.checkout'
  default_recipient = 'server'

  serializable_attributes = ['item_barcode', 'user_barcode', 'tag_type']
  item_barcode = ''
  user_barcode = 0
  tag_type = 'rfid'

  def __init__(self, item_barcode: str, user_barcode: str, tag_type: str, client: WebSocket = None, recipient: WebSocket = None, event_id: str = None):
    self.item_barcode = item_barcode
    self.user_barcode = user_barcode
    self.tag_type = tag_type if tag_type else self.tag_type
    super().__init__(event=self.event, client=client, recipient=recipient, event_id=event_id)
    self.validate_params()

class LECheckOutComplete(LEvent):
  event = 'check-out-complete'
  default_recipient = 'client'

  serializable_attributes = ['item_barcode', 'user_barcode', 'tag_type', 'status', 'states']
  item_barcode = ''
  user_barcode = 0
  tag_type = 'rfid'
  states = {}
  status = Status.NOT_SET

  def __init__(self, item_barcode: str, user_barcode: str, tag_type: str, status: Status, states: dict = {}, client: WebSocket = None, recipient: WebSocket = None, event_id: str = None):
    self.item_barcode = item_barcode
    self.user_barcode = user_barcode
    self.tag_type = tag_type if tag_type else self.tag_type
    self.status = status
    self.states = states
    super().__init__(event=self.event, client=client, recipient=recipient, event_id=event_id)
    self.validate_params()

class LECheckIn(LEvent):
  event = 'check-in'
  default_handler = 'lainuri.websocket_handlers.checkin.checkin'
  default_recipient = 'server'

  serializable_attributes = ['item_barcode', 'tag_type']
  item_barcode = ''
  tag_type = 'rfid'

  def __init__(self, item_barcode: str, tag_type: str, client: WebSocket = None, recipient: WebSocket = None, event_id: str = None):
    self.item_barcode = item_barcode
    self.tag_type = tag_type if tag_type else self.tag_type
    super().__init__(event=self.event, client=client, recipient=recipient, event_id=event_id)
    self.validate_params()

class LECheckInComplete(LEvent):
  event = 'check-in-complete'
  default_recipient = 'client'

  serializable_attributes = ['item_barcode', 'status', 'states', 'tag_type']
  item_barcode = ''
  tag_type = 'rfid'
  states = {}
  status = Status.NOT_SET

  def __init__(self, item_barcode: str, tag_type: str, status: Status, states: dict = {}, client: WebSocket = None, recipient: WebSocket = None, event_id: str = None):
    self.item_barcode = item_barcode
    self.tag_type = tag_type if tag_type else self.tag_type
    self.states = states
    self.status = status
    super().__init__(event=self.event, client=client, recipient=recipient, event_id=event_id)
    self.validate_params()

class LESetTagAlarm(LEvent):
  event = 'set-tag-alarm'
  default_handler = 'lainuri.websocket_handlers.tag_alarm.set_tag_alarm'
  default_recipient = 'server'

  serializable_attributes = ['item_barcode', 'on']
  item_barcode = ''
  on = True

  def __init__(self, item_barcode: str, on: bool, client: WebSocket = None, recipient: WebSocket = None, event_id: str = None):
    self.item_barcode = item_barcode
    self.on = on
    super().__init__(event=self.event, client=client, recipient=recipient, event_id=event_id)
    self.validate_params()

class LESetTagAlarmComplete(LEvent):
  event = 'set-tag-alarm-complete'
  default_recipient = 'client'

  serializable_attributes = ['item_barcode', 'on', 'status', 'states']
  item_barcode = ''
  on = True
  states = {}
  status = Status.NOT_SET

  def __init__(self, item_barcode: str, on: bool, status: Status, states: dict = {}, client: WebSocket = None, recipient: WebSocket = None, event_id: str = None):
    self.item_barcode = item_barcode
    self.on = on
    self.states = states
    self.status = status
    super().__init__(event=self.event, client=client, recipient=recipient, event_id=event_id)
    self.validate_params()

class LERingtonePlay(LEvent):
  event = 'ringtone-play'
  default_handler = 'lainuri.websocket_handlers.ringtone.ringtone_play'
  default_recipient = 'server'

  serializable_attributes = ['ringtone_type', 'ringtone']
  ringtone_type = ''
  ringtone = ''

  def __init__(self, ringtone_type: str = None, ringtone: str = None, client: WebSocket = None, recipient: WebSocket = None, event_id: str = None):
    self.ringtone_type = ringtone_type
    self.ringtone = ringtone
    message = {key: getattr(self, key) for key in self.serializable_attributes}
    super().__init__(event=self.event, message=message, client=client, recipient=recipient, event_id=event_id)

class LERingtonePlayComplete(LEvent):
  event = 'ringtone-play-complete'
  default_recipient = 'client'

  serializable_attributes = ['ringtone_type', 'ringtone', 'states', 'status']
  ringtone_type = ''
  ringtone = ''
  states = {}
  status = Status.NOT_SET

  def __init__(self, status: Status, ringtone_type: str = None, ringtone: str = None, states: dict = {}, client: WebSocket = None, recipient: WebSocket = None, event_id: str = None):
    self.ringtone_type = ringtone_type
    self.ringtone = ringtone
    self.states = states
    self.status = status
    message = {key: getattr(self, key) for key in self.serializable_attributes}
    super().__init__(event=self.event, message=message, client=client, recipient=recipient, event_id=event_id)

class LEBarcodeRead(LEvent):
  event = 'barcode-read'
  default_recipient = 'client'

  serializable_attributes = ['barcode', 'tag']
  barcode = ''
  tag = {}

  def __init__(self, barcode: str, client: WebSocket = None, recipient: WebSocket = None, event_id: str = None):
    self.barcode = barcode
    self.tag = koha_api.get_fleshed_item_record(barcode, tag_type='barcode')
    super().__init__(event=self.event, client=client, recipient=recipient, event_id=event_id)
    self.validate_params()

class LEConfigWrite(LEvent):
  event = 'config-write'
  default_handler = 'lainuri.websocket_handlers.config.write_config'
  default_recipient = 'server'

  serializable_attributes = ['variable', 'new_value']
  variable = ''
  new_value = ''

  def __init__(self, variable: str, new_value: str, client: WebSocket = None, recipient: WebSocket = None, event_id: str = None):
    self.variable = variable
    self.new_value = new_value
    message = {key: getattr(self, key) for key in self.serializable_attributes}
    super().__init__(event=self.event, message=message, client=client, recipient=recipient, event_id=event_id)
    self.validate_params()

class LEPrintRequest(LEvent):
  event = 'print-request'
  default_handler = 'lainuri.websocket_handlers.printer.print_receipt'
  default_recipient = 'server'

  serializable_attributes = ['receipt_type', 'items', 'user_barcode']
  receipt_type = ''
  items = []
  user_barcode = ''

  def __init__(self, receipt_type: str, items: list, user_barcode: str, client: WebSocket = None, recipient: WebSocket = None, event_id: str = None):
    self.receipt_type = receipt_type
    self.items = items
    self.user_barcode = user_barcode
    super().__init__(event=self.event, client=client, recipient=recipient, event_id=event_id)

class LEPrintResponse(LEvent):
  event = 'print-response'
  default_recipient = 'client'

  serializable_attributes = ['receipt_type', 'items', 'user_barcode', 'printable_sheet', 'states', 'status']
  receipt_type = ''
  items = []
  user_barcode = ''
  printable_sheet = ''
  states = {}
  status = Status.NOT_SET

  def __init__(self, receipt_type: str, items: list, user_barcode: str, printable_sheet: str, status: Status, states: dict = {}, client: WebSocket = None, recipient: WebSocket = None, event_id: str = None):
    self.receipt_type = receipt_type
    self.items = items
    self.user_barcode = user_barcode
    self.printable_sheet = printable_sheet
    self.states = states
    self.status = status
    super().__init__(event=self.event, client=client, recipient=recipient, event_id=event_id)

class LERFIDTagsLost(LEvent):
  event = 'rfid-tags-lost'
  default_recipient = 'client'

  serializable_attributes = ['tags_lost','tags_present']
  tags_present = []

  def __init__(self, tags_lost: list, tags_present: list, client: WebSocket = None, recipient: WebSocket = None, event_id: str = None):
    self.tags_present = tags_present
    self.tags_lost = tags_lost
    message = {
      'tags_lost': [{**tag.to_ui(), **koha_api.get_fleshed_item_record(tag.iso25680_get_primary_item_identifier())} for tag in self.tags_lost],
      'tags_present': [{**tag.to_ui(), **koha_api.get_fleshed_item_record(tag.iso25680_get_primary_item_identifier())} for tag in self.tags_present],
    }
    super().__init__(event=self.event, message=message, client=client, recipient=recipient, event_id=event_id)

class LERFIDTagsNew(LEvent):
  event = 'rfid-tags-new'
  default_recipient = 'client'

  serializable_attributes = ['tags_new','tags_present']
  tags_present = []

  def __init__(self, tags_new: list, tags_present: list, client: WebSocket = None, recipient: WebSocket = None, event_id: str = None):
    self.tags_present = tags_present
    self.tags_new = tags_new
    message = {
      'tags_new': [{**tag.to_ui(), **koha_api.get_fleshed_item_record(tag.iso25680_get_primary_item_identifier())} for tag in self.tags_new],
      'tags_present': [{**tag.to_ui(), **koha_api.get_fleshed_item_record(tag.iso25680_get_primary_item_identifier())} for tag in self.tags_present],
    }
    super().__init__(event=self.event, message=message, client=client, recipient=recipient, event_id=event_id)
    self.validate_params()

class LERFIDTagsPresent(LEvent):
  event = 'rfid-tags-present'
  default_recipient = 'client'

  serializable_attributes = ['tags_present']
  tags_present = []

  def __init__(self, tags_present: list, client: WebSocket = None, recipient: WebSocket = None, event_id: str = None):
    self.tags_present = tags_present
    message = {
      'tags_present': [{**tag.to_ui(), **koha_api.get_fleshed_item_record(tag.iso25680_get_primary_item_identifier())} for tag in tags_present],
    }
    super().__init__(event=self.event, message=message, client=client, recipient=recipient, event_id=event_id)
    self.validate_params()

class LEServerStatusRequest(LEvent):
  event = 'server-status-request'
  default_handler = 'lainuri.websocket_handlers.status.status_request'
  default_recipient = 'server'

class LEServerStatusResponse(LEvent):
  event = 'server-status-response'
  default_recipient = 'client'

  serializable_attributes = ['barcode_reader_status', 'thermal_printer_status', 'rfid_reader_status', 'touch_screen_status']
  barcode_reader_status = {}
  thermal_printer_status = {}
  rfid_reader_status = {}
  touch_screen_status = {}

  def __init__(self, barcode_reader_status: dict, thermal_printer_status: dict, rfid_reader_status: dict, touch_screen_status: dict, client: WebSocket = None, recipient: WebSocket = None, event_id: str = None):
    self.barcode_reader_status = barcode_reader_status
    self.thermal_printer_status = thermal_printer_status
    self.rfid_reader_status = rfid_reader_status
    self.touch_screen_status = touch_screen_status
    message = {key: getattr(self, key) for key in self.serializable_attributes}
    super().__init__(event=self.event, message=message, client=client, recipient=recipient, event_id=event_id)
    self.validate_params()

class LEUserLoggingIn(LEvent):
  event = 'user-logging-in'
  default_recipient = 'server'

  serializable_attributes = ['username', 'password']
  username = ''
  password = ''

  def __init__(self, username: str = None, password:str = None, client: WebSocket = None, recipient: WebSocket = None, event_id: str = None):
    self.password = password
    message = {key: getattr(self, key) for key in self.serializable_attributes}
    super().__init__(event=self.event, message=message, client=client, recipient=recipient, event_id=event_id)
    #self.validate_params()

class LEUserLoginComplete(LEvent):
  event = 'user-login-complete'
  default_recipient = 'client'

  serializable_attributes = ['firstname', 'surname', 'user_barcode', 'states', 'status']
  firstname = ''
  surname = ''
  user_barcode = ''
  states = {}
  status = Status.NOT_SET

  def __init__(self, firstname: str, surname: str, user_barcode: str, status: Status, states: dict = {}, client: WebSocket = None, recipient: WebSocket = None, event_id: str = None):
    self.firstname = firstname
    self.surname = surname
    self.user_barcode = user_barcode
    self.states = states
    self.status = status
    message = {key: getattr(self, key) for key in self.serializable_attributes}
    super().__init__(event=self.event, message=message, client=client, recipient=recipient, event_id=event_id)
    self.validate_params()

class LEUserLoginAbort(LEvent):
  event = 'user-login-abort'
  default_recipient = 'server'

  def __init__(self, client: WebSocket = None, recipient: WebSocket = None, event_id: str = None):
    super().__init__(event=self.event, message=None, client=client, recipient=recipient, event_id=event_id)

class LERegisterClient(LEvent):
  event = 'register-client'
  default_recipient = 'client'

  def __init__(self, client: WebSocket = None, recipient: WebSocket = None, event_id: str = None):
    super().__init__(event=self.event, message=None, client=client, recipient=recipient, event_id=event_id)

class LEDeregisterClient(LEvent):
  event = 'deregister-client'
  default_recipient = 'client'

  def __init__(self, client: WebSocket = None, recipient: WebSocket = None, event_id: str = None):
    super().__init__(event=self.event, message=None, client=client, recipient=recipient, event_id=event_id)
class LETestMockDevices(LEvent):
  event = 'test-mock-devices'
  default_handler = 'lainuri.websocket_handlers.test.mock_devices'
  default_recipient = 'client'

  def __init__(self, client: WebSocket = None, recipient: WebSocket = None, event_id: str = None):
    super().__init__(event=self.event, message=None, client=client, recipient=recipient, event_id=event_id)




eventname_to_eventclass = {}
def map_eventname_to_eventclass():
  g = globals()
  for key in g:
    imported = g[key]
    if type(imported) == type and getattr(imported, '__init__', None): # This is a class type, since it has a constructor
      eventname = imported.__dict__.get('event', None)
      if eventname: eventname_to_eventclass[eventname] = imported
map_eventname_to_eventclass()

def parseEventFromWebsocketMessage(raw_data: str, client: WebSocket):
  data = json.loads(raw_data)
  event_class = eventname_to_eventclass.get(data['event'], None)
  if not event_class: raise Exception(f"Event '{data['event']}' doesn't map to a event class")
  if not data['event_id']: raise Exception(f"Event '{raw_data}' is missing event_id!")
  instance_data = {'client': client, 'recipient': None, 'event_id': data['event_id']}
  serializable_attributes = event_class.__dict__.get('serializable_attributes', None)
  parameters = {}
  if serializable_attributes:
    parameters = {attr: data['message'].get(attr, None) for attr in serializable_attributes}
  try:
    return event_class(**parameters, **instance_data)
  except Exception as e:
    raise type(e)(f"Creating event '{event_class}' with parameters '{parameters}' instance_data '{instance_data}' failed:\n" + traceback.format_exc())
