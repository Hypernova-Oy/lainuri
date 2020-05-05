from lainuri.config import get_config
from lainuri.logging_context import logging
log = logging.getLogger(__name__)

from lainuri.constants import Status
import lainuri.event
import lainuri.event_queue
import lainuri.hs_k33

import subprocess
import threading
import time
import traceback

event_poll_for_receipt_torn = threading.Event()
print_receipt_event = None
kill = False

def start_polling(event: lainuri.event.LEPrintRequest):
  global event_poll_for_receipt_torn, print_receipt_event
  event_poll_for_receipt_torn.set()
  print_receipt_event = event

def end_polling():
  global event_poll_for_receipt_torn, print_receipt_event
  event_poll_for_receipt_torn.clear()
  print_receipt_event = None

def emit_event():
  global print_receipt_event
  lainuri.event_queue.push_event(
    lainuri.event.LEPrintResponse(
      receipt_type=print_receipt_event.receipt_type, items=print_receipt_event.items, user_barcode=print_receipt_event.user_barcode, printable_sheet='',
      status=Status.SUCCESS,
    )
  )

def printer_status_daemon():
  global event_poll_for_receipt_torn, print_receipt_event, kill
  log.info(f"Thermal printer status polling thread starting")

  hs_k33 = lainuri.hs_k33.get_printer()

  while(threading.main_thread().isAlive()):
    if kill:
      kill = False
      break
    if not event_poll_for_receipt_torn.wait(1): # This allows the running thread to receive and handle other commands, instead of being endlessly stuck at the event wait.
      continue


    try:
      if not hs_k33.is_paper_torn_away():
        emit_event()
        end_polling()
      else:
        time.sleep(0.1)
    except Exception as e:
      log.error(f"Error polling for LEPrintRequest-event '{print_receipt_event.__dict__}'. exception:\n{traceback.format_exc()}")
      emit_event()
      end_polling()


  log.info(f"Terminating Thermal printer status polling thread")
  exit(0)
