from lainuri.config import get_config
from lainuri.logging_context import logging
log = logging.getLogger(__name__)

from simple_websocket_server import WebSocketServer, WebSocket

import json
import _thread as thread
import time
import traceback

from lainuri.constants import Status
import lainuri.helpers
import lainuri.event
import lainuri.event_queue
from lainuri.koha_api import koha_api
import lainuri.locale
from lainuri.exception import NoResults
import lainuri.exception.ils as exception_ils
import lainuri.rfid_reader
import lainuri.barcode_reader

## Import all handlers, because the handle_events_loop dynamically invokes them
import lainuri.websocket_handlers.auth
import lainuri.websocket_handlers.checkin
import lainuri.websocket_handlers.checkout
import lainuri.websocket_handlers.config
import lainuri.websocket_handlers.locale
import lainuri.websocket_handlers.logging
import lainuri.websocket_handlers.printer
import lainuri.websocket_handlers.ringtone
import lainuri.websocket_handlers.status
import lainuri.websocket_handlers.tag_alarm
import lainuri.websocket_handlers.test



clients = []

"""
states:
get_items: rfid tags and barcodes are interpreted as item barcodes and are pushed to the UI
           with enriched information from the library system
user-logging-in: barcode reads are interpreted as user reading his/hers library card.
                 Thus we try to login to library system and return with results.
"""
state = 'get_items'
def set_state(new_state: str):
  global state
  log.info(f"New state '{new_state}'")
  state = new_state

def handle_events_loop():
  while(1):
    try:
      handle_one_event()
    except Exception as e:
      log.error(f"Handling event failed!")
      log.exception(e)
      #lainuri.event_queue.push_event(lainuri.event.LEvent('exception', {'exception': traceback.format_exc()}, recipient=event.recipient, event_id=lainuri.helpers.null_safe_lookup(event, ['event_id'])))

def handle_one_event(timeout: int = None) -> lainuri.event.LEvent:
  event = lainuri.event_queue.pop_event(timeout=timeout)
  if type(event) != lainuri.event.LELogSend and type(event) != lainuri.event.LELogReceived: log.info(f"Handling event {event.to_string()}")

  # Messages originating from the Lainuri UI
  if event.recipient == 'server' or (not(event.recipient) and event.default_recipient == 'server'):
    if event.default_handler: eval(event.default_handler)(event)
    elif event.event == 'user-logging-in':
      set_state('user-logging-in')
    elif event.event == 'user-login-abort':
      set_state('get_items')
    elif event.event == 'config-getpublic':
      lainuri.websocket_handlers.config.get_public_configs(event)
    elif event.event == 'register-client':
      register_client(event)
    elif event.event == 'deregister-client':
      deregister_client(event)
    elif event.event == 'exception':
      log.error(f"Client exception: '{event.message}'")
    else:
      raise Exception(f"Unknown event '{event.__dict__}'")

  # Messages from the server to the UI
  elif event.recipient == 'client' or (not(event.recipient) and event.default_recipient == 'client'):
    if event.event in ['user-login-complete'] and event.status == Status.SUCCESS:
      set_state('get_items')
    message_clients(event)

  else:
    raise Exception(f"Don't know how to route event '{event.event_id or ''}':\n  '{event.__dict__}'")

  return event

def message_clients(event: lainuri.event.LEvent):
  for client in clients:
    if (event.recipient and event.recipient == client) or (not(event.recipient) and not(client == event.client)):
      payload = event.serialized or event.serialize_ws()
      if type(event) != lainuri.event.LELogSend and type(event) != lainuri.event.LELogReceived: log.info(f"Message to client '{client.address}': '{payload}'")
      client.send_message(payload)

def register_client(event):
  log.info(f"Registering client: '{event}'")
  global clients
  clients.append(event.client)

  lainuri.websocket_handlers.status.get_rfid_tags_present(event)

  lainuri.websocket_handlers.config.get_public_configs()

  log.info(f"Registered client: '{event}'. Clients present '{len(clients)}'")

def deregister_client(event):
  log.info(f"Deregistering client: '{event}'")
  global clients
  clients.remove(event.client)
  log.info(f"Deregistered client: '{event}'. Clients present '{len(clients)}'")


class SimpleChat(WebSocket):
  def handle(self):
    event = None
    try:
      try:
        event = lainuri.event.parseEventFromWebsocketMessage(self.data, self)
        lainuri.event_queue.push_event(event)
      except Exception as e:
        log.error(f"Handling payload failed!: {self.data}")
        log.exception(e)
        lainuri.event_queue.push_event(lainuri.event.LEvent('exception', {'exception': traceback.format_exc()}, recipient=self, event_id=lainuri.helpers.null_safe_lookup(event, ['event_id'])))
    except Exception as e2:
      log.exception(e2)

  def connected(self):
    event = None
    try:
      try:
        event = lainuri.event.LERegisterClient(client=self, recipient='server')
        lainuri.event_queue.push_event(event)
      except Exception as e:
        log.error(f"Handling payload failed!: {self.data}")
        log.exception(e)
        lainuri.event_queue.push_event(lainuri.event.LEvent('exception', {'exception': traceback.format_exc()}, recipient=self, event_id=lainuri.helpers.null_safe_lookup(event, ['event_id'])))
    except Exception as e2:
      log.exception(e2)

  def handle_close(self):
    event = None
    try:
      try:
        event = lainuri.event.LEDeregisterClient(client=self, recipient='server')
        lainuri.event_queue.push_event(event)
      except Exception as e:
        log.error(f"Handling payload failed!: {self.data}")
        log.exception(e)
        lainuri.event_queue.push_event(lainuri.event.LEvent('exception', {'exception': traceback.format_exc()}, recipient=event.recipient, event_id=lainuri.helpers.null_safe_lookup(event, ['event_id'])))
    except Exception as e2:
      log.exception(e2)

def start():

  lainuri.locale.verify_locales_installed()
  lainuri.config.image_overloads_handle()

  # Other devices need data from the Koha API, so we need to make sure we have a working connection before
  # letting device threads to fork.
  if koha_api:
    koha_api.authenticate()

  if get_config('devices.rfid-reader.enabled'):
    rfid_reader = lainuri.rfid_reader.get_rfid_reader()
    rfid_reader.start_polling_rfid_tags()
  else:
    log.info("RFID reader is disabled by config")

  start_barcode_reader()

  thread.start_new_thread(handle_events_loop, ())

  port = int(get_config('server.port'))
  hostname = get_config('server.hostname')
  log.info(f"Starting WebSocketServer on '{hostname}:{port}'")
  server = WebSocketServer(hostname, port, SimpleChat)
  server.serve_forever()

def start_barcode_reader():
  if get_config('devices.barcode-reader.enabled'):
    barcode_reader = lainuri.barcode_reader.get_BarcodeReader()
    barcode_reader.start_polling_barcodes(handle_barcode_read)
    return barcode_reader
  else:
    log.info("WGC300 reader is disabled by config")
  return None

def handle_barcode_read(barcode: str):
  if (lainuri.websocket_server.state == 'user-logging-in'):
    lainuri.websocket_handlers.auth.login_user(barcode)
  else:
    lainuri.event_queue.push_event(lainuri.event.LEBarcodeRead(barcode))
