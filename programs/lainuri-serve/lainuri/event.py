from lainuri.config import get_config
from lainuri.logging_context import logging
log = logging.getLogger(__name__)
import lainuri.pretty as lp

import base64
from simple_websocket_server import WebSocket
import json
import time
import traceback

from lainuri.constants import SortBin, Status
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

  def __init__(self, event: str = None, client: WebSocket = None, recipient: WebSocket = None, event_id: str = None):
    self.event = event
    self.client = client
    self.recipient = recipient
    self.event_id = event_id
    self.timestamp = time.time()
    if not(self.event_id) and self.event: self.event_id = get_event_id(self.event)

  def serialize_ws(self):
    return json.dumps({
      'event': self.event,
      'message': {key: getattr(self, key) for key in self.serializable_attributes},
      'event_id': self.event_id,
    })

  def validate_params(self):
    for attribute_name in self.serializable_attributes:
      if not(hasattr(self, attribute_name)):
        self.throw_missing_attribute(attribute_name)

  def throw_missing_attribute(self, attribute_name: str):
    class_name = type(self)
    raise Exception(f"{class_name}():> Missing attribute '{attribute_name}'")

  def to_string(self):
    #return f"event_id='{self.event_id}' " + str({key: getattr(self, key) for key in self.serializable_attributes})
    return lp.pformat(self.__dict__)

class LEAdminModeEnter(LEvent):
  event = 'admin-mode-enter'
  default_recipient = 'client'

  serializable_attributes = []

  def __init__(self, client: WebSocket = None, recipient: WebSocket = None, event_id: str = None):
    super().__init__(event=self.event, client=client, recipient=recipient, event_id=event_id)
    self.validate_params()

class LEAdminModeLeave(LEvent):
  event = 'admin-mode-leave'
  default_handler = 'lainuri.websocket_handlers.status.admin_mode_leave'
  default_recipient = 'server'

  serializable_attributes = []

  def __init__(self, client: WebSocket = None, recipient: WebSocket = None, event_id: str = None):
    super().__init__(event=self.event, client=client, recipient=recipient, event_id=event_id)
    self.validate_params()

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

  serializable_attributes = ['item_barcode', 'sort_to', 'tag_type', 'status', 'states']
  item_barcode = ''
  sort_to = SortBin.NOT_SET
  tag_type = 'rfid'
  states = {}
  status = Status.NOT_SET

  def __init__(self, item_barcode: str, sort_to: SortBin, tag_type: str, status: Status, states: dict = {}, client: WebSocket = None, recipient: WebSocket = None, event_id: str = None):
    self.item_barcode = item_barcode
    self.sort_to = sort_to
    self.tag_type = tag_type if tag_type else self.tag_type
    self.states = states
    self.status = status
    super().__init__(event=self.event, client=client, recipient=recipient, event_id=event_id)
    self.validate_params()

class LELocaleSet(LEvent):
  event = 'locale-set'
  default_handler = 'lainuri.websocket_handlers.locale.set_locale'
  default_recipient = 'server'

  serializable_attributes = ['locale_code']
  locale_code = ''

  def __init__(self, locale_code: str, client: WebSocket = None, recipient: WebSocket = None, event_id: str = None):
    self.locale_code = locale_code
    super().__init__(event=self.event, client=client, recipient=recipient, event_id=event_id)
    self.validate_params()

class LETransactionHistoryRequest(LEvent):
  event = 'transaction-history-request'
  default_handler = 'lainuri.websocket_handlers.transaction_history.list_some'
  default_recipient = 'server'

  serializable_attributes = ['start_time','end_time']
  start_time = 0
  end_time = 0

  def __init__(self, start_time: int, end_time: int, client: WebSocket = None, recipient: WebSocket = None, event_id: str = None):
    self.start_time = start_time
    self.end_time = end_time
    super().__init__(event=self.event, client=client, recipient=recipient, event_id=event_id)
    self.validate_params()

class LETransactionHistoryResponse(LEvent):
  event = 'transaction-history-response'
  default_recipient = 'client'

  serializable_attributes = ['transactions', 'status', 'states']
  transactions = []
  states = {}
  status = Status.NOT_SET

  def __init__(self, transactions, status: Status, states: dict = {}, client: WebSocket = None, recipient: WebSocket = None, event_id: str = None):
    self.transactions = transactions
    self.states = states
    self.status = status
    super().__init__(event=self.event, client=client, recipient=recipient, event_id=event_id)
    self.validate_params()

  def to_string(self):
    o = {**self.__dict__}
    o['transactions'] = len(o['transactions'])
    return lp.pformat(o)

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

class LERingtoneList(LEvent):
  event = 'ringtone-list'
  default_handler = 'lainuri.websocket_handlers.ringtone.ringtone_list'
  default_recipient = 'server'

  serializable_attributes = []

class LERingtoneListResponse(LEvent):
  event = 'ringtone-list-response'
  default_recipient = 'client'

  serializable_attributes = ['rtttls', 'states', 'status']
  rtttls = {}
  states = {}
  status = Status.NOT_SET

  def __init__(self, rtttls: dict, status: Status, states: dict = {}, client: WebSocket = None, recipient: WebSocket = None, event_id: str = None):
    self.rtttls = rtttls
    self.states = states
    self.status = status
    super().__init__(event=self.event, client=client, recipient=recipient, event_id=event_id)

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
    super().__init__(event=self.event, client=client, recipient=recipient, event_id=event_id)

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
    super().__init__(event=self.event, client=client, recipient=recipient, event_id=event_id)

class LEBarcodeRead(LEvent):
  event = 'barcode-read'
  default_recipient = 'client'

  serializable_attributes = ['barcode', 'tag']
  barcode = ''
  tag = {}

  def __init__(self, barcode: str, client: WebSocket = None, recipient: WebSocket = None, event_id: str = None):
    self.barcode = barcode
    self.tag = {'tag_type': 'barcode', **koha_api.get_fleshed_item_record(barcode)}
    super().__init__(event=self.event, client=client, recipient=recipient, event_id=event_id)
    self.validate_params()

class LEConfigGetpublic(LEvent):
  event = 'config-getpublic'
  default_handler = 'lainuri.websocket_handlers.config.get_public_configs'
  default_recipient = 'server'

  def __init__(self, client: WebSocket = None, recipient: WebSocket = None, event_id: str = None):
    super().__init__(event=self.event, client=client, recipient=recipient, event_id=event_id)
    self.validate_params()

class LEConfigGetpublic_Response(LEvent):
  event = 'config-getpublic-response'
  default_recipient = 'client'

  serializable_attributes = ['config']
  config = {}

  def __init__(self, config: dict, client: WebSocket = None, recipient: WebSocket = None, event_id: str = None):
    self.config = config
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
    super().__init__(event=self.event, client=client, recipient=recipient, event_id=event_id)
    self.validate_params()

class LEConfigWriteResponse(LEvent):
  event = 'config-write-response'
  default_recipient = 'client'

  serializable_attributes = ['variable', 'new_value', 'old_value']
  variable = ''
  new_value = ''
  old_value = ''

  def __init__(self, variable: str, new_value: str, old_value: str, client: WebSocket = None, recipient: WebSocket = None, event_id: str = None):
    self.variable = variable
    self.new_value = new_value
    self.old_value = old_value
    super().__init__(event=self.event, client=client, recipient=recipient, event_id=event_id)
    self.validate_params()

class LEItemBibFullDataRequest(LEvent):
  event = 'itembib-fulldata-request'
  default_handler = 'lainuri.websocket_handlers.status.itembib_fulldata'
  default_recipient = 'server'

  serializable_attributes = ['barcodes']

  barcodes = []

  def __init__(self, barcodes, client: WebSocket = None, recipient: WebSocket = None, event_id: str = None):
    self.barcodes = barcodes
    super().__init__(event=self.event, client=client, recipient=recipient, event_id=event_id)
    self.validate_params()

class LEItemBibFullDataResponse(LEvent):
  event = 'itembib-fulldata-response'
  default_recipient = 'client'

  serializable_attributes = ['item_bibs']

  item_bibs = []

  def __init__(self, item_bibs, client: WebSocket = None, recipient: WebSocket = None, event_id: str = None):
    self.item_bibs = item_bibs
    super().__init__(event=self.event, client=client, recipient=recipient, event_id=event_id)
    self.validate_params()

class LELogSend(LEvent):
  event = 'log-send'
  default_handler = 'lainuri.websocket_handlers.logging.write_external_log'
  default_recipient = 'server'

  serializable_attributes = ['messages']

  def __init__(self, messages, client: WebSocket = None, recipient: WebSocket = None, event_id: str = None):
    self.messages = messages
    super().__init__(event=self.event, client=client, recipient=recipient, event_id=event_id)
    self.validate_params()

class LELogReceived(LEvent):
  event = 'log-received'
  default_recipient = 'client'

  serializable_attributes = ['status', 'states']
  states = {}
  status = Status.NOT_SET

  def __init__(self, status, states, client: WebSocket = None, recipient: WebSocket = None, event_id: str = None):
    self.states = states
    self.status = status
    super().__init__(event=self.event, client=client, recipient=recipient, event_id=event_id)
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

class LEPrintTemplateList(LEvent):
  event = 'print-template-list'
  default_handler = 'lainuri.websocket_handlers.printer.list_templates'
  default_recipient = 'server'

class LEPrintTemplateListResponse(LEvent):
  event = 'print-template-list-response'
  default_recipient = 'client'

  serializable_attributes = ['templates', 'status', 'states']
  templates = {}
  states = {}
  status = Status.NOT_SET

  def __init__(self, templates: list, status: Status, states: dict = {}, client: WebSocket = None, recipient: WebSocket = None, event_id: str = None):
    self.templates = templates
    self.states = states
    self.status = status
    super().__init__(event=self.event, client=client, recipient=recipient, event_id=event_id)

class LEPrintTemplateSave(LEvent):
  event = 'print-template-save'
  default_handler = 'lainuri.websocket_handlers.printer.save_template'
  default_recipient = 'server'

  serializable_attributes = ['id', 'type', 'locale_code', 'template']
  id = None,
  type = '',
  locale_code = ''
  template = ''

  def __init__(self, id: int, type: str, locale_code: str, template: str, client: WebSocket = None, recipient: WebSocket = None, event_id: str = None):
    self.id = id
    self.type = type
    self.locale_code = locale_code
    self.template = template
    super().__init__(event=self.event, client=client, recipient=recipient, event_id=event_id)

class LEPrintTemplateSaveResponse(LEvent):
  event = 'print-template-save-response'
  default_recipient = 'client'

  serializable_attributes = ['id', 'type', 'locale_code', 'status', 'states']
  id = None
  type = ''
  locale_code = ''
  states = {}
  status = Status.NOT_SET

  def __init__(self, id: int, type: str, locale_code: str, status: Status, states: dict = {}, client: WebSocket = None, recipient: WebSocket = None, event_id: str = None):
    self.id = id
    self.type = type
    self.locale_code = locale_code
    self.status = status
    self.states = states
    super().__init__(event=self.event, client=client, recipient=recipient, event_id=event_id)

class LEPrintTestRequest(LEvent):
  event = 'print-test-request'
  default_handler = 'lainuri.websocket_handlers.printer.test_print'
  default_recipient = 'server'

  serializable_attributes = ['template', 'data', 'css', 'real_print']
  template = ''
  data = {}
  css = ''
  real_print = False

  def __init__(self, template: str, data: dict, css: str, real_print: bool, client: WebSocket = None, recipient: WebSocket = None, event_id: str = None):
    self.template = template
    self.data = data
    self.css = css
    self.real_print = real_print
    super().__init__(event=self.event, client=client, recipient=recipient, event_id=event_id)

class LEPrintTestResponse(LEvent):
  event = 'print-test-response'
  default_recipient = 'client'

  serializable_attributes = ['image', 'states', 'status']
  image = bytes()
  states = {}
  status = Status.NOT_SET

  def __init__(self, image: bytes, status: Status, states: dict = {}, client: WebSocket = None, recipient: WebSocket = None, event_id: str = None):
    self.image = base64.b64encode(image).decode('utf-8')
    self.states = states
    self.status = status
    super().__init__(event=self.event, client=client, recipient=recipient, event_id=event_id)

  def to_string(self): #image can be massive, so skip it
    s2 = dict(self.__dict__)
    s2['image'] = len(self.image)
    return lp.pformat(s2)

class LERFIDTagsLost(LEvent):
  event = 'rfid-tags-lost'
  default_recipient = 'client'

  serializable_attributes = ['tags_lost','tags_present']
  tags_present = []

  def __init__(self, tags_lost: list, tags_present: list, client: WebSocket = None, recipient: WebSocket = None, event_id: str = None):
    self.tags_present = [{**tag.to_ui(), 'item_barcode': tag.iso25680_get_primary_item_identifier()} for tag in tags_present]
    self.tags_lost =    [{**tag.to_ui(), 'item_barcode': tag.iso25680_get_primary_item_identifier()} for tag in tags_lost   ]
    super().__init__(event=self.event, client=client, recipient=recipient, event_id=event_id)

class LERFIDTagsNew(LEvent):
  event = 'rfid-tags-new'
  default_recipient = 'client'

  serializable_attributes = ['tags_new','tags_present', 'status', 'states']
  tags_present = []
  states = {}
  status = Status.NOT_SET

  def __init__(self, tags_new: list, tags_present: list, status: Status, states: dict = {}, client: WebSocket = None, recipient: WebSocket = None, event_id: str = None):
    self.tags_present = [{**tag.to_ui(), 'item_barcode': tag.iso25680_get_primary_item_identifier()} for tag in tags_present]
    self.tags_new =     [{**tag.to_ui(), 'item_barcode': tag.iso25680_get_primary_item_identifier()} for tag in tags_new    ]
    self.states = states
    self.status = status
    super().__init__(event=self.event, client=client, recipient=recipient, event_id=event_id)
    self.validate_params()

class LERFIDTagsPresentRequest(LEvent):
  event = 'rfid-tags-present-request'
  default_handler = 'lainuri.websocket_handlers.status.get_rfid_tags_present'
  default_recipient = 'server'

  serializable_attributes = []

  def __init__(self, client: WebSocket = None, recipient: WebSocket = None, event_id: str = None):
    super().__init__(event=self.event, client=client, recipient=recipient, event_id=event_id)

class LERFIDTagsPresent(LEvent):
  event = 'rfid-tags-present'
  default_recipient = 'client'

  serializable_attributes = ['tags_present']
  tags_present = []

  def __init__(self, tags_present: list, client: WebSocket = None, recipient: WebSocket = None, event_id: str = None):
    self.tags_present = [{**tag.to_ui(), **koha_api.get_fleshed_item_record(tag.iso25680_get_primary_item_identifier())} for tag in tags_present]
    super().__init__(event=self.event, client=client, recipient=recipient, event_id=event_id)
    self.validate_params()

class LEServerStatusRequest(LEvent):
  event = 'server-status-request'
  default_handler = 'lainuri.websocket_handlers.status.status_request'
  default_recipient = 'server'

  def __init__(self, client: WebSocket = None, recipient: WebSocket = None, event_id: str = None):
    super().__init__(event=self.event, client=client, recipient=recipient, event_id=event_id)

class LEServerStatusResponse(LEvent):
  event = 'server-status-response'
  default_recipient = 'client'

  serializable_attributes = ['statuses']

  def __init__(self, statuses: dict, client: WebSocket = None, recipient: WebSocket = None, event_id: str = None):
    self.statuses = statuses
    super().__init__(event=self.event, client=client, recipient=recipient, event_id=event_id)
    self.validate_params()

class LEUserLoggingIn(LEvent):
  event = 'user-logging-in'
  default_recipient = 'server'

  serializable_attributes = ['username', 'password']
  username = ''
  password = ''

  def __init__(self, username: str = None, password:str = None, client: WebSocket = None, recipient: WebSocket = None, event_id: str = None):
    self.password = password
    super().__init__(event=self.event, client=client, recipient=recipient, event_id=event_id)
    #self.validate_params()

class LEUserLoginComplete(LEvent):
  event = 'user-login-complete'
  default_recipient = 'client'

  serializable_attributes = ['firstname', 'surname', 'user_barcode', 'status', 'states']
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
    super().__init__(event=self.event, client=client, recipient=recipient, event_id=event_id)
    self.validate_params()

class LEUserLoginAbort(LEvent):
  event = 'user-login-abort'
  default_recipient = 'server'

  def __init__(self, client: WebSocket = None, recipient: WebSocket = None, event_id: str = None):
    super().__init__(event=self.event, client=client, recipient=recipient, event_id=event_id)

class LERegisterClient(LEvent):
  event = 'register-client'
  default_recipient = 'server'

  def __init__(self, client: WebSocket = None, recipient: WebSocket = None, event_id: str = None):
    super().__init__(event=self.event, client=client, recipient=recipient, event_id=event_id)

class LEDeregisterClient(LEvent):
  event = 'deregister-client'
  default_recipient = 'server'

  def __init__(self, client: WebSocket = None, recipient: WebSocket = None, event_id: str = None):
    super().__init__(event=self.event, client=client, recipient=recipient, event_id=event_id)

class LETestMockDevices(LEvent):
  event = 'test-mock-devices'
  default_handler = 'lainuri.websocket_handlers.test.mock_devices'
  default_recipient = 'client'

  def __init__(self, client: WebSocket = None, recipient: WebSocket = None, event_id: str = None):
    super().__init__(event=self.event, client=client, recipient=recipient, event_id=event_id)

class LEException(LEvent):
  event = 'exception'

  serializable_attributes = ['exception']
  exception = Exception()

  def __init__(self, exception, client: WebSocket = None, recipient: WebSocket = None, event_id: str = None):
    if isinstance(exception, Exception):
      self.exception = traceback.format_exc()
    else:
      self.exception = exception

    super().__init__(event=self.event, client=client, recipient=recipient, event_id=event_id)
    self.validate_params()


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
    event = event_class(**parameters, **instance_data)
    return event
  except Exception as e:
    raise type(e)(f"Creating event '{event_class}' with parameters '{parameters}' instance_data '{instance_data}' failed:\n" + traceback.format_exc())
