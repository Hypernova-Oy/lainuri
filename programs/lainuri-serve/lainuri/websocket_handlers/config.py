from lainuri.config import get_config
from lainuri.logging_context import logging
log = logging.getLogger(__name__)

import json

import lainuri.event
import lainuri.event_queue

def get_public_configs(event=None):
  try:
    lainuri.event_queue.push_event(lainuri.event.LEConfigGetpublic_Response(
      config=lainuri.config.get_public_configs(),
    ))
  except Exception as e:
    log.exception(f"Exception at {__name__}")
    lainuri.event_queue.push_event(
      lainuri.event.LEConfigGetpublic_Response(
        config={},
        status=Status.ERROR,
        states={'exception': {
          'type': type(e).__name__,
          'trace': str(e)}
        },
      )
    )

def write_config(event):
  try:
    lainuri.event_queue.push_event(lainuri.event.LEConfigWriteResponse(
      **lainuri.config.write_config(event.variable, event.new_value)
    ))
  except Exception as e:
    log.exception(f"Exception at {__name__}")
    lainuri.event_queue.push_event(
      lainuri.event.LEConfigWriteResponse(
        config={},
        status=Status.ERROR,
        states={'exception': {
          'type': type(e).__name__,
          'trace': str(e)}
        },
      )
    )
