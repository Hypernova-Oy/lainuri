from lainuri.config import get_config
from lainuri.logging_context import logging
log = logging.getLogger(__name__)

from lainuri.constants import Status
import lainuri.event
import lainuri.event_queue
import lainuri.hs_k33
from lainuri.threadbase import Threadbase

import subprocess
import threading
import time
import traceback


def start_polling_for_receipt_torn(req_event: lainuri.event.LEPrintRequest):
  daemon = get_daemon()
  daemon.notify(req_event)
  return daemon

def printer_status_daemon(req_event: lainuri.event.LEPrintRequest):
  global daemon
  hs_k33 = lainuri.hs_k33.get_printer()

  while(threading.main_thread().is_alive()):
    if daemon.killswitch:
      break
    try:
      if hs_k33.is_paper_torn_away():
        lainuri.event_queue.push_event(
          lainuri.event.LEPrintResponse(
            receipt_type=req_event.receipt_type, items=req_event.items, user_barcode=req_event.user_barcode, printable_sheet='',
            status=Status.SUCCESS,
          )
        )
        break
      else:
        time.sleep(0.5)
    except Exception as e:
      log.exception("Error polling for LEPrintRequest-event")
      lainuri.event_queue.push_event(
        lainuri.event.LEPrintResponse(
          receipt_type=req_event.receipt_type, items=req_event.items, user_barcode=req_event.user_barcode, printable_sheet='',
          status=Status.ERROR,
          states={'exception': {
            'type': type(e).__name__,
            'trace': str(e)}
          },
        )
      )
      break

daemon = None
def get_daemon():
  global daemon
  if daemon: return daemon
  daemon = Threadbase(name='ThermalPrinter', worker_method=printer_status_daemon, listen_for_event=True)
  return daemon

def stop_daemon():
  global daemon
  if not daemon: return
  daemon.kill()
  daemon = None
