from lainuri.config import get_config
from lainuri.logging_context import logging
log = logging.getLogger(__name__)

import json

import lainuri.event
import lainuri.event_queue

def get_public_configs(event=None):
  lainuri.event_queue.push_event(lainuri.event.LEConfigGetpublic_Response(
    config=lainuri.config.get_public_configs(),
  ))

def write_config(event):
  lainuri.event_queue.push_event(lainuri.event.LEConfigWriteResponse(
    **lainuri.config.write_config(event.variable, event.new_value)
  ))
