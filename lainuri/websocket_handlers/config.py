import lainuri.config
from lainuri.logging_context import logging
log = logging.getLogger(__name__)

import json

import lainuri.websocket_server
from lainuri.event import LEvent

def get_public_configs(event=None):
  lainuri.websocket_server.push_event(LEvent(
    'config-getpublic-response',
    {'config': lainuri.config.get_public_configs()},
  ))

def write_config(event):
  lainuri.websocket_server.push_event(LEvent(
    'config-write-response',
    lainuri.config.write_config(event.message['variable'], event.message['new_value']),
  ))
