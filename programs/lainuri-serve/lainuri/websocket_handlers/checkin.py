from lainuri.config import get_config
from lainuri.logging_context import logging
log = logging.getLogger(__name__)

import traceback

#from lainuri.event import LEvent # Cannot import this even for type safety, due to circular dependency

from lainuri.koha_api import koha_api
import lainuri.websocket_server
import lainuri.event
import lainuri.websocket_handlers.checkout

def checkin(event):
  try:
    (status, states) = koha_api.checkin(event.item_barcode)

    try:
      lainuri.websocket_handlers.checkout.set_tag_gate_alarm(event, True)
    except Exception as e:
      log.exception(e)
      status = 'error'
      states['set_tag_gate_alarm_failed'] = traceback.format_exc()

    lainuri.websocket_server.push_event(
      lainuri.event.LECheckInComplete(event.item_barcode, event.tag_type, status, states)
    )
  except Exception:
    lainuri.websocket_server.push_event(
      lainuri.event.LECheckInComplete(event.item_barcode, event.tag_type, 'failed', {
        'exception': traceback.format_exc(),
      })
    )
