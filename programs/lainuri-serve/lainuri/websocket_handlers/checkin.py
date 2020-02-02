from lainuri.config import get_config
from lainuri.logging_context import logging
log = logging.getLogger(__name__)

import traceback

#from lainuri.event import LEvent # Cannot import this even for type safety, due to circular dependency

from lainuri.koha_api import koha_api
import lainuri.websocket_server
import lainuri.event

def checkin(event):
  # Checkout to Koha
  statuses = koha_api.checkin(event.item_barcode)
  if statuses['status'] == 'failed':
    lainuri.websocket_server.push_event(
      lainuri.event.LECheckInFailed(event.item_barcode, statuses)
    )
    return

  lainuri.websocket_server.push_event(
    lainuri.event.LECheckInComplete(event.item_barcode, statuses)
  )
