from lainuri.config import get_config
from lainuri.logging_context import logging
log = logging.getLogger(__name__)

from simple_websocket_server import WebSocketServer, WebSocket

import json
import _thread as thread
import time
import traceback

import lainuri.helpers
import lainuri.event
import lainuri.event_queue
from lainuri.koha_api import koha_api
from lainuri.exceptions import InvalidUser, NoResults
import lainuri.rfid_reader
import lainuri.barcode_reader

## Import all handlers, because the handle_events_loop dynamically invokes them
import lainuri.websocket_handlers.checkin
import lainuri.websocket_handlers.checkout
import lainuri.websocket_handlers.config
import lainuri.websocket_handlers.printer
import lainuri.websocket_handlers.ringtone
import lainuri.websocket_handlers.status
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
      event = lainuri.event_queue.pop_event()
      log.info(f"Handling event '{event.event_id or ''}':\n  '{event.__dict__}'")

      # Messages originating from the Lainuri UI
      if event.client:
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
      else:
        if event.event in ['user-logged-in','user-login-failed']:
          set_state('get_items')
        message_clients(event)
    except Exception as e:
      log.error(f"Handling event failed!: {event}")
      log.exception(e)
      lainuri.event_queue.push_event(lainuri.event.LEvent('exception', {'exception': traceback.format_exc()}, recipient=event.recipient, event_id=lainuri.helpers.null_safe_lookup(event, ['event_id'])))

def message_clients(event: lainuri.event.LEvent):
  for client in clients:
    if (event.recipient and event.recipient == client) or (not(event.recipient) and not(client == event.client)):
      payload = event.serialize_ws()
      log.info(f"Message to client '{client.address}': '{payload}'")
      client.send_message(payload)

def register_client(event):
  log.info(f"Registering client: '{event}'")
  global clients
  clients.append(event.client)

  lainuri.event_queue.push_event(lainuri.event.LERFIDTagsPresent(
    tags_present=lainuri.rfid_reader.get_current_inventory_status(),
    recipient=event.client)
  )

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
        event = lainuri.event.LEvent('register-client', {}, self)
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
        event = lainuri.event.LEvent('deregister-client', {}, self)
        lainuri.event_queue.push_event(event)
      except Exception as e:
        log.error(f"Handling payload failed!: {self.data}")
        log.exception(e)
        lainuri.event_queue.push_event(lainuri.event.LEvent('exception', {'exception': traceback.format_exc()}, recipient=event.recipient, event_id=lainuri.helpers.null_safe_lookup(event, ['event_id'])))
    except Exception as e2:
      log.exception(e2)

def start():

  # Other devices need data from the Koha API, so we need to make sure we have a working connection before
  # letting device threads to fork.
  if koha_api:
    koha_api.authenticate()

  if get_config('devices.rfid-reader.enabled'):
    rfid_reader = lainuri.rfid_reader.RFID_Reader()
    rfid_reader.start_polling_rfid_tags()
  else:
    log.info("RFID reader is disabled by config")

  if get_config('devices.barcode-reader.enabled'):
    barcode_reader = lainuri.barcode_reader.BarcodeReader()
    barcode_reader.start_polling_barcodes(handle_barcode_read)
  else:
    log.info("WGC300 reader is disabled by config")

  thread.start_new_thread(handle_events_loop, ())

  server = WebSocketServer('localhost', 53153, SimpleChat)
  server.serve_forever()

def handle_barcode_read(barcode: str):
  if (lainuri.websocket_server.state == 'user-logging-in'):
    lainuri.websocket_server.login_user(barcode)
  else:
    lainuri.event_queue.push_event(lainuri.event.LEBarcodeRead(barcode))

def login_user(user_barcode: str):
  try:
    borrower = koha_api.get_borrower(user_barcode=user_barcode)
    if koha_api.authenticate_user(user_barcode=user_barcode):
      lainuri.event_queue.push_event(
        lainuri.event.LEUserLoggedIn(
          firstname=borrower['firstname'],
          surname=borrower['surname'],
          user_barcode=borrower['cardnumber'],
        )
      )
    else:
      raise Exception("Login failed! koha_api should throw an Exception instead!")
  except InvalidUser as e:
    lainuri.event_queue.push_event(lainuri.event.LEUserLoginFailed(exception=str(e)))
  except NoResults as e:
    lainuri.event_queue.push_event(lainuri.event.LEUserLoginFailed(exception=str(e)))
  except Exception as e:
    lainuri.event_queue.push_event(lainuri.event.LEUserLoginFailed(exception=e))
