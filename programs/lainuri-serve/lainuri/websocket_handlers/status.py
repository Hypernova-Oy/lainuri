from lainuri.config import get_config
from lainuri.logging_context import logging
log = logging.getLogger(__name__)

from lainuri.constants import Status
import lainuri.event
import lainuri.event_queue
import lainuri.koha_api as koha_api
import lainuri.status
import lainuri.rfid_reader

def admin_mode_leave(event = None):
  import lainuri.websocket_server
  lainuri.status.set_lainuri_state('get_items')

def get_rfid_tags_present(event = None):
  try:
    lainuri.event_queue.push_event(lainuri.event.LERFIDTagsPresent(tags_present=lainuri.rfid_reader.get_current_inventory_status()))
  except Exception as e:
    log.exception(f"Exception at {__name__}")
    lainuri.event_queue.push_event(
      lainuri.event.LERFIDTagsPresent(
        tags_present=[],
        status=Status.ERROR,
        states={'exception': {
          'type': type(e).__name__,
          'trace': str(e)}
        },
      )
    )

def itembib_fulldata(event):
  lainuri.event_queue.push_event(lainuri.event.LEItemBibFullDataResponse(
    item_bibs=[koha_api.get_fleshed_item_record(barcode) for barcode in event.barcodes]
  ))

def status_request(event = None):
  try:
    lainuri.status.poll_software_version()
    lainuri.event_queue.push_event(
      lainuri.event.LEServerStatusResponse(
        statuses=lainuri.status.statuses
      )
    )
  except Exception as e:
    log.exception(f"Exception at {__name__}")
    lainuri.event_queue.push_event(
      lainuri.event.LEServerStatusResponse(
        statuses=lainuri.status.statuses,
        status=Status.ERROR,
        states={'exception': {
          'type': type(e).__name__,
          'trace': str(e)}
        },
      )
    )
