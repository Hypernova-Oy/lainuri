from lainuri.config import get_config
from lainuri.logging_context import logging
log = logging.getLogger(__name__)

from lainuri.constants import Status
import lainuri.event
import lainuri.event_queue
import lainuri.status
import lainuri.rfid_reader


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
