from lainuri.config import get_config
from lainuri.logging_context import logging
log = logging.getLogger(__name__)

import traceback

#from lainuri.event import LEvent # Cannot import this even for type safety, due to circular dependency

from lainuri.koha_api import koha_api
from lainuri.constants import Status
import lainuri.event
import lainuri.event_queue
import lainuri.rfid_reader as rfid

def checkin(event):
  try:
    (status, states) = koha_api.checkin(event.item_barcode)
    lainuri.event_queue.push_event(
      lainuri.event.LECheckInComplete(
        item_barcode=event.item_barcode,
        tag_type=event.tag_type,
        status=status,
        states=states,
      )
    )
  except Exception as e:
    log.exception(f"Exception at {__name__}")
    lainuri.event_queue.push_event(
      lainuri.event.LECheckInComplete(
        item_barcode=event.item_barcode,
        tag_type=event.tag_type,
        status=Status.ERROR,
        states={'exception': {
          'type': type(e).__name__,
          'trace': str(e)}
        },
      )
    )
