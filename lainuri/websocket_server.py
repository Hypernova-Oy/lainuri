import lainuri.config
from lainuri.logging_context import logging
log = logging.getLogger(__name__)

from simple_websocket_server import WebSocketServer, WebSocket
import _thread as thread
import threading
import time
import json

from lainuri.event import LEvent, LEventException
import lainuri.websocket_handlers.ringtone
import lainuri.websocket_handlers.config
import lainuri.rfid_reader



clients = []
events = []

def push_event(event: LEvent):
  log.info(f"New event '{event.__dict__}'")
  events.append(event)

  # Messages originating from the Lainuri UI
  if event.client:
    if event.event == 'ringtone-play':
      if lainuri.config.get('devices.ringtone-player.enabled'):
        lainuri.websocket_handlers.ringtone.ringtone_play(event)
    elif event.event == 'config-getpublic':
      lainuri.websocket_handlers.config.get_public_configs(event)
    elif event.event == 'config-write':
      lainuri.websocket_handlers.config.write_config(event)
    elif event.event == 'register-client':
      register_client(event)
    elif event.event == 'deregister-client':
      deregister_client(event)
    else:
      raise Exception(f"Unknown event '{event.__dict__}'")

  # Messages from the server to the UI
  else:
    message_clients(event)

def message_clients(event: LEvent):
  for client in clients:
    if (event.recipient and event.recipient == client) or (not(event.recipient) and not(client == event.client)):
      log.info(f"Message to client '{client.address}': '{event.message}'")
      client.send_message(json.dumps(event.message))



def register_client(event):
  global clients
  clients.append(event.client)
  tag_serials = lainuri.rfid_reader.get_current_inventory_status()
  lainuri.websocket_server.push_event(LEvent("rfid-tags-new", tag_serials, recipient=event.client))

def deregister_client(event):
  global clients
  clients.remove(event.client)

class SimpleChat(WebSocket):
  def handle(self):
    try:
      push_event(LEvent().from_ws(self))
    except Exception as e:
      log.exception(e)
      push_event(LEventException('exception', None, e))
      raise e

  def connected(self):
    try:
      push_event(LEvent('register-client', {}, self))
    except Exception as e:
      log.exception(e)
      push_event(LEventException('exception', None, e))
      raise e

  def handle_close(self):
    try:
      push_event(LEvent('deregister-client', {}, self))
    except Exception as e:
      log.exception(e)
      push_event(LEventException('exception', None, e))
      raise e

def start():
  lainuri.rfid_reader.start()
  server = WebSocketServer('localhost', 12345, SimpleChat)
  server.serve_forever()
