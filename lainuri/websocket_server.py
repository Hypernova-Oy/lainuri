from lainuri.config import get_config
from lainuri.logging_context import logging
log = logging.getLogger(__name__)

from simple_websocket_server import WebSocketServer, WebSocket

import _thread as thread
import threading
import time
import traceback

from lainuri.event import LEvent, LERFIDTagsPresent
import lainuri.websocket_handlers.ringtone
import lainuri.websocket_handlers.config
import lainuri.websocket_handlers.test
import lainuri.rfid_reader
import lainuri.WGCUsb300AT


clients = []
events = []

def push_event(event: LEvent):
  log.info(f"New event '{event.__dict__}'")
  events.append(event)

  # Messages originating from the Lainuri UI
  if event.client:
    if event.event == 'ringtone-play':
      lainuri.websocket_handlers.ringtone.ringtone_play(event)
    elif event.event == 'config-getpublic':
      lainuri.websocket_handlers.config.get_public_configs(event)
    elif event.event == 'config-write':
      lainuri.websocket_handlers.config.write_config(event)
    elif event.event == 'register-client':
      register_client(event)
    elif event.event == 'deregister-client':
      deregister_client(event)
    elif event.event == 'test-mock-devices':
      lainuri.websocket_handlers.test.mock_devices(event)
    elif event.event == 'exception':
      log.error(f"Client exception: '{event.message}'")
    else:
      raise Exception(f"Unknown event '{event.__dict__}'")

  # Messages from the server to the UI
  else:
    message_clients(event)

def message_clients(event: LEvent):
  for client in clients:
    if (event.recipient and event.recipient == client) or (not(event.recipient) and not(client == event.client)):
      payload = event.serialize_ws()
      log.info(f"Message to client '{client.address}': '{payload}'")
      client.send_message(payload)



def register_client(event):
  global clients
  clients.append(event.client)

  tags_present = lainuri.rfid_reader.get_current_inventory_status()
  lainuri.websocket_server.push_event(LERFIDTagsPresent(tags_present, recipient=event.client))

  lainuri.websocket_handlers.config.get_public_configs()

def deregister_client(event):
  global clients
  clients.remove(event.client)

event_id: int = 0
def get_event_id(event_name: str) -> str:
  global event_id
  event_id += 1
  return event_name + '-' + str(event_id)

class SimpleChat(WebSocket):
  def handle(self):
    event = None
    try:
      try:
        event = LEvent().from_ws(self)
        push_event(event)
      except Exception as e:
        log.exception(e)
        push_event(LEvent('exception', {'exception': traceback.format_exc()}, recipient=self, event_id=event.event_id))
    except Exception as e2:
      log.exception(e2)

  def connected(self):
    event = None
    try:
      try:
        event = LEvent('register-client', {}, self)
        push_event(event)
      except Exception as e:
        log.exception(e)
        push_event(LEvent('exception', {'exception': traceback.format_exc()}, recipient=self, event_id=event.event_id))
    except Exception as e2:
      log.exception(e2)

  def handle_close(self):
    event = None
    try:
      try:
        event = LEvent('deregister-client', {}, self)
        push_event(event)
      except Exception as e:
        log.exception(e)
        push_event(LEvent('exception', {'exception': traceback.format_exc()}, recipient=self, event_id=event.event_id))
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
    barcode_reader.start_polling_barcodes()
  else:
    log.info("WGC300 reader is disabled by config")

  server = WebSocketServer('localhost', 53153, SimpleChat)
  server.serve_forever()
