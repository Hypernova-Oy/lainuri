from lainuri.config import get_config
from lainuri.logging_context import logging
log = logging.getLogger(__name__)

from lainuri.constants import Status
import lainuri.event
import lainuri.event_queue
import lainuri.rfid_reader

ils_connection_status = Status.SUCCESS

def get_rfid_tags_present(event = None):
  lainuri.event_queue.push_event(lainuri.event.LERFIDTagsPresent(tags_present=lainuri.rfid_reader.get_current_inventory_status()))

def set_ils_connection_status(status: Status):
  global ils_connection_status
  if status == ils_connection_status: return
  log.info(f"ils_connection_status set from '{ils_connection_status}' to '{status}'")
  ils_connection_status = status

def status_request(event):
  lainuri.event_queue.push_event(
    lainuri.event.LEServerStatusResponse(
      barcode_reader_status=Status.SUCCESS,
      thermal_printer_status=Status.SUCCESS,
      rfid_reader_status=Status.SUCCESS,
      touch_screen_status=Status.SUCCESS,
      ils_connection_status=ils_connection_status,
    )
  )
