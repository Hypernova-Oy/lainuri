"""
Keeps track of the device and app statuses
Separate this from the weboscket_handler implementation to reduce coupling between components
"""

from lainuri.config import get_config, get_lainuri_conf_dir
from lainuri.logging_context import logging
log = logging.getLogger(__name__)

from lainuri.constants import Status
import lainuri.event
import lainuri.event_queue

import subprocess

def update_status(status: str, value: Status):
  global statuses
  if statuses[status] != value:
    log.info(f"status '{status}' set from '{statuses[status]}' to '{value}'")
    statuses[status] = value

    lainuri.status.poll_software_version()
    lainuri.event_queue.push_event(
      lainuri.event.LEServerStatusResponse(
        statuses=statuses
      )
    )

software_version_check_countdown = 0 # Don't check for version every time status is updated
def poll_software_version():
  global software_version_check_countdown
  if software_version_check_countdown == 0:
    software_version_check_countdown = 10
    update_status('software_version', get_software_version())
  software_version_check_countdown -= 1
  return statuses['software_version']

def get_software_version():
  try:
    return subprocess.check_output(f"git log -1 --pretty=format:%H", shell=True).decode('utf8')
  except Exception as e:
    log.exception(f"Exception getting software version")
    return Status.ERROR

statuses = {
  'barcode_reader_status': Status.SUCCESS,
  'thermal_printer_status': Status.SUCCESS,
  'thermal_printer_paper_status': Status.SUCCESS,
  'rfid_reader_status': Status.SUCCESS,
  'touch_screen_status': Status.SUCCESS,
  'ils_connection_status': Status.SUCCESS,
  'ils_credentials_status': Status.SUCCESS,
  'software_version': None,
}
