from lainuri.config import get_config
from lainuri.logging_context import logging
log = logging.getLogger(__name__)

from lainuri.constants import Status
import lainuri.event
import lainuri.event_queue
import lainuri.status
import lainuri.rfid_reader


def get_rfid_tags_present(event = None):
  lainuri.event_queue.push_event(lainuri.event.LERFIDTagsPresent(tags_present=lainuri.rfid_reader.get_current_inventory_status()))

def status_request(event):
  lainuri.event_queue.push_event(
    lainuri.event.LEServerStatusResponse(
      statuses=lainuri.status.statuses
    )
  )
