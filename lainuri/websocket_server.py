from lainuri.config import get_config
from lainuri.logging_context import logging
log = logging.getLogger(__name__)

from simple_websocket_server import WebSocketServer, WebSocket

import json
import _thread as thread
import threading
import time
import traceback

import lainuri.event
from lainuri.koha_api import koha_api
from lainuri.exceptions import InvalidUser, NoResults

import lainuri.websocket_handlers.config
import lainuri.rfid_reader
import lainuri.WGCUsb300AT

eventname_to_eventclass = {}
for key in lainuri.event.__dict__:
  imported = lainuri.event.__dict__[key]
  if type(imported) == type and getattr(imported, '__init__', None): # This is a class type, since it has a constructor
    eventname = imported.__dict__.get('event', None)
    if eventname: eventname_to_eventclass[eventname] = imported

def ParseEventFromWebsocketMessage(raw_data: str, client: WebSocket):
  data = json.loads(raw_data)
  event_class = eventname_to_eventclass.get(data['event'], None)
  if not event_class: raise Exception(f"Event '{data['event']}' doesn't map to a event class")
  if not data['event_id']: raise Exception(f"Event '{raw_data}' is missing event_id!")
  instance_data = {'client': client, 'recipient': None, 'event_id': data['event_id']}
  serializable_attributes = event_class.__dict__.get('serializable_attributes', None)
  parameters = {}
  if serializable_attributes:
    parameters = {attr: data['message'].get(attr, None) for attr in serializable_attributes}
  instance = event_class(**parameters, **instance_data)
  return instance



clients = []
events = []
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

def push_event(event: lainuri.event.LEvent):
  global events
  log.info(f"New event '{event.__dict__}'")
  events.append(event)

  # Messages originating from the Lainuri UI
  if event.client:
    if event.default_handler: event.default_handler()
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

def message_clients(event: lainuri.event.LEvent):
  for client in clients:
    if (event.recipient and event.recipient == client) or (not(event.recipient) and not(client == event.client)):
      payload = event.serialize_ws()
      log.info(f"Message to client '{client.address}': '{payload}'")
      client.send_message(payload)

def register_client(event):
  global clients
  clients.append(event.client)

  tags_present = lainuri.rfid_reader.get_current_inventory_status()
  lainuri.websocket_server.push_event(lainuri.event.LERFIDTagsPresent(tags_present, recipient=event.client))

  lainuri.websocket_handlers.config.get_public_configs()

def deregister_client(event):
  global clients
  clients.remove(event.client)


class SimpleChat(WebSocket):
  def handle(self):
    event = None
    try:
      try:
        event = ParseEventFromWebsocketMessage(self.data, self)
        push_event(event)
      except Exception as e:
        log.exception(e)
        push_event(lainuri.event.LEvent('exception', {'exception': traceback.format_exc()}, recipient=self, event_id=event.event_id))
    except Exception as e2:
      log.exception(e2)

  def connected(self):
    event = None
    try:
      try:
        event = lainuri.event.LEvent('register-client', {}, self)
        push_event(event)
      except Exception as e:
        log.exception(e)
        push_event(lainuri.event.LEvent('exception', {'exception': traceback.format_exc()}, recipient=self, event_id=event.event_id))
    except Exception as e2:
      log.exception(e2)

  def handle_close(self):
    event = None
    try:
      try:
        event = lainuri.event.LEvent('deregister-client', {}, self)
        push_event(event)
      except Exception as e:
        log.exception(e)
        push_event(lainuri.event.LEvent('exception', {'exception': traceback.format_exc()}, recipient=self, event_id=event.event_id))
    except Exception as e2:
      log.exception(e2)

def start():

  if get_config('devices.rfid-reader.enabled'):
    rfid_reader = lainuri.rfid_reader.RFID_Reader()
    rfid_reader.start_polling_rfid_tags()
  else:
    log.info("RFID reader is disabled by config")

  if get_config('devices.barcode-reader.enabled'):
    barcode_reader = lainuri.WGCUsb300AT.BarcodeReader()
    barcode_reader.start_polling_barcodes(handle_barcode_read)
  else:
    log.info("WGC300 reader is disabled by config")

  if koha_api:
    koha_api.authenticate()

  server = WebSocketServer('localhost', 53153, SimpleChat)
  server.serve_forever()

def handle_barcode_read(barcode: str):
  if (lainuri.websocket_server.state == 'user-logging-in'):
    lainuri.websocket_server.login_user(barcode)
  else:
    lainuri.websocket_server.push_event(lainuri.event.LEBarcodeRead(barcode))

def login_user(user_barcode: str):
  try:
    borrower = koha_api.get_borrower(user_barcode=user_barcode)
    if koha_api.authenticate_user(user_barcode=user_barcode):
      lainuri.websocket_server.push_event(
        lainuri.event.LEUserLoggedIn(
          firstname=borrower['firstname'],
          surname=borrower['surname'],
          user_barcode=borrower['cardnumber'],
        )
      )
    else:
      raise Exception("Login failed! koha_api should throw an Exception instead!")
  except InvalidUser as e:
    lainuri.websocket_server.push_event(lainuri.event.LEUserLoginFailed(e=str(e)))
  except NoResults as e:
    lainuri.websocket_server.push_event(lainuri.event.LEUserLoginFailed(e=str(e)))
  except Exception as e:
    lainuri.websocket_server.push_event(lainuri.event.LEUserLoginFailed(e=e))
