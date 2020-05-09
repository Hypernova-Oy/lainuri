from lainuri.config import get_config
from lainuri.logging_context import logging
log = logging.getLogger(__name__)

import subprocess
import traceback

from lainuri.constants import Status
import lainuri.event as le
import lainuri.event_queue
from lainuri.koha_api import koha_api
import lainuri.printer

def print_receipt(event):
  borrower = None
  printable_sheet = None

  try:
    printable_sheet = None

    if event.receipt_type == 'check-out':
      printable_sheet = lainuri.printer.print_check_out_receipt(user_barcode=event.user_barcode, items=event.items)
    elif event.receipt_type == 'check-in':
      printable_sheet = lainuri.printer.print_check_in_receipt(user_barcode=event.user_barcode, items=event.items)
    else:
      raise ValueError(f"print_receipt() Unknown receipt_type '{event.receipt_type}'!")

    lainuri.event_queue.push_event(
      le.LEPrintResponse(
        receipt_type=event.receipt_type, items=event.items, user_barcode=event.user_barcode, printable_sheet=printable_sheet,
        status=Status.SUCCESS, # We are waiting for the end-user to tear off the receipt, see lainuri.printer.status
      )
    )

    #lainuri.printer.status.start_polling_for_receipt_torn(event)

  except Exception as e:
    log.exception(f"Exception at {__name__}")
    lainuri.event_queue.push_event(
      le.LEPrintResponse(
        receipt_type=event.receipt_type, items=event.items, user_barcode=event.user_barcode, printable_sheet=printable_sheet or None,
        status=Status.ERROR,
        states={'exception': {
          'type': type(e).__name__,
          'trace': str(e)}
        },
      )
    )
