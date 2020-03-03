from lainuri.config import get_config
from lainuri.logging_context import logging
log = logging.getLogger(__name__)

import lainuri.event as le
import lainuri.event_queue

def status_request(event):
  lainuri.event_queue.push_event(
    le.LEServerStatusResponse(
      barcode_reader_status={
        'status': 'pending',
      },
      thermal_printer_status={
        'status': 'pending',
      },
      rfid_reader_status={
        'status': 'pending',
      },
      touch_screen_status={
        'status': 'pending',
      })
  )
