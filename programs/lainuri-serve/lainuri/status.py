"""
Keeps track of the device and app statuses
Separate this from the weboscket_handler implementation to reduce coupling between components
"""

from lainuri.config import get_config, get_lainuri_conf_dir
from lainuri.logging_context import logging
log = logging.getLogger(__name__)

from lainuri.constants import Status

statuses = {
  'barcode_reader_status': Status.SUCCESS,
  'thermal_printer_status': Status.SUCCESS,
  'thermal_printer_paper_status': Status.SUCCESS,
  'rfid_reader_status': Status.SUCCESS,
  'touch_screen_status': Status.SUCCESS,
  'ils_connection_status': Status.SUCCESS,
}

def update_status(status: str, value: Status):
  global statuses
  if statuses[status] != value:
    log.info(f"status '{status}' set from '{statuses[status]}' to '{value}'")
    statuses[status] = value
