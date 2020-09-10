from lainuri.config import get_config
from lainuri.logging_context import logging
log = logging.getLogger(__name__)

from simple_websocket_server import WebSocketServer, WebSocket

import json
import queue
import _thread as thread
import threading
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
import lainuri.printer
import lainuri.printer.status
import lainuri.rfid_reader
import lainuri.rpc_daemon
import lainuri.barcode_reader
import lainuri.rtttl_player
import lainuri.status
from lainuri.threadbase import Threadbase

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


def handle_one_event_daemon():
  try:
    return handle_one_event(2)
  except queue.Empty as e:
    pass

def handle_one_event(timeout: int = None, event: lainuri.event.LEvent = None) -> lainuri.event.LEvent:
  if not event: event = lainuri.event_queue.pop_event(timeout=timeout)
  if type(event) != lainuri.event.LELogSend and type(event) != lainuri.event.LELogReceived:
    log.info(f"Handling event {event.to_string()}")

  # Messages originating from the Lainuri UI
  if event.recipient == 'server' or (not(event.recipient) and event.default_recipient == 'server'):
    if event.default_handler: eval(event.default_handler)(event)
    elif event.event == 'user-logging-in':
      lainuri.status.set_lainuri_state('user-logging-in')
    elif event.event == 'user-login-abort':
      lainuri.status.set_lainuri_state('get_items')
    elif event.event == 'register-client':
      register_client(event)
    elif event.event == 'deregister-client':
      deregister_client(event)
    elif event.event == 'exception':
      log.error(f"Client exception: '{event.to_string()}'")
    else:
      raise Exception(f"Unknown event '{event.__dict__}'")

  # Messages from the server to the UI
  elif event.recipient == 'client' or (not(event.recipient) and event.default_recipient == 'client'):
    if event.event in ['user-login-complete'] and event.status == Status.SUCCESS:
      lainuri.status.set_lainuri_state('get_items')
    message_clients(event)

  else:
    raise Exception(f"Don't know how to route event '{event.event_id or ''}':\n  '{event.__dict__}'")

  return event

def message_clients(event: lainuri.event.LEvent):
  if log.isEnabledFor(logging.INFO):
    if type(event) != lainuri.event.LELogSend and type(event) != lainuri.event.LELogReceived:
      log.info(f"Message to clients '{[client.address for client in clients]}' event_id '{event.event_id}'")

  for client in clients:
    if (event.recipient and event.recipient == client) or (not(event.recipient) and not(client == event.client)):
      client.send_message(event.serialize_ws())

def register_client(event):
  log.info(f"Registering client: '{event}'")
  global clients
  clients.append(event.client)

  try:
    lainuri.websocket_handlers.config.get_public_configs()
  except Exception:
    log.exception("Exception registering client, get_public_configs()")
  try:
    lainuri.websocket_handlers.status.get_rfid_tags_present(event)
  except Exception:
    log.exception("Exception registering client, get_rfid_tags_present()")
  try:
    lainuri.websocket_handlers.status.status_request()
  except Exception:
    log.exception("Exception registering client, status_request()")

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
        log.exception(f"Handling payload failed!: {self.data}")
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
        log.exception(f"Handling payload failed!: {self.data}")
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
        log.exception(f"Handling payload failed!: {self.data}")
        lainuri.event_queue.push_event(lainuri.event.LEvent('exception', {'exception': traceback.format_exc()}, recipient=event.recipient, event_id=lainuri.helpers.null_safe_lookup(event, ['event_id'])))
    except Exception as e2:
      log.exception(e2)

subthreads = {}
def start(ws_daemon: bool = False) -> bool:
  global subthreads

  lainuri.locale.verify_locales_installed()
  lainuri.config.image_overloads_handle()

  try:
    if get_config('devices.rfid-reader.enabled'):
      lainuri.rfid_reader.get_rfid_reader().start_polling_rfid_tags()
    else:
      log.info("RFID reader is disabled by config")
  except Exception as e:
    log.exception("Failed to start the RFID reader during webserver boot!")

  lainuri.barcode_reader.init(lainuri.websocket_server.handle_barcode_read).start_polling_barcodes()

  lainuri.event_queue.init(event_handler=lainuri.websocket_server.handle_one_event_daemon).start()

  lainuri.rpc_daemon.start_daemon()

  lainuri.rtttl_player.get_player().start()

  if get_config('devices.thermal-printer.enabled'):
    #lainuri.printer.status.get_daemon().start() #Disable this for now to eliminate race conditions when printing receipts
    pass

  port = int(get_config('server.port'))
  hostname = get_config('server.hostname')
  log.info(f"Starting WebSocketServer on '{hostname}:{port}'")
  ws_server = WebSocketServer(hostname, port, SimpleChat)
  if (ws_daemon):
    subthreads['server'] = Threadbase(name='WebSocketServer', worker_method=ws_server.handle_request())
    subthreads['server'].start()
  else:
    ws_server.serve_forever()

  return True

def stop() -> bool:
  lainuri.rfid_reader.get_rfid_reader().stop_polling_rfid_tags()
  lainuri.barcode_reader.get_BarcodeReader().stop_polling_barcodes()
  lainuri.event_queue.get_daemon().kill()
  lainuri.rpc_daemon.stop_daemon()
  lainuri.rtttl_player.get_player().kill()
  if get_config('devices.thermal-printer.enabled'):
    #lainuri.printer.status.get_daemon().kill()
    pass
  subthreads['server'].kill()

  lainuri.rfid_reader.get_rfid_reader().daemon.join(10)
  lainuri.barcode_reader.get_BarcodeReader().daemon.join(10)
  lainuri.event_queue.get_daemon().join(10)
  if lainuri.rpc_daemon.get_daemon(): lainuri.rpc_daemon.get_daemon().join(10)
  lainuri.rtttl_player.get_player().join(10)
  if get_config('devices.thermal-printer.enabled'):
    #lainuri.printer.status.get_daemon().join(10)
    pass
  subthreads['server'].join(10)
  return True

def handle_barcode_read(bcr: lainuri.barcode_reader.BarcodeReader, barcode: str):
  if get_config('admin.master-barcode') == barcode:
    lainuri.status.set_lainuri_state('admin', barcode)
  elif (lainuri.status.lainuri_state == 'user-logging-in'):
    lainuri.websocket_handlers.auth.login_user(barcode)
  else:
    lainuri.event_queue.push_event(lainuri.event.LEBarcodeRead(barcode))
