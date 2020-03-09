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

    if event.receipt_type == 'check-out':

      borrower = koha_api.get_borrower(event.user_barcode)
      printable_sheet = koha_api.receipt(borrower['borrowernumber'])
      lainuri.printer.print_html(printable_sheet)
      lainuri.event_queue.push_event(
        le.LEPrintResponse(
          receipt_type=event.receipt_type, items=event.items, user_barcode=event.user_barcode, printable_sheet=printable_sheet,
          status=Status.SUCCESS,
        )
      )

    elif event.receipt_type == 'check-in':

      printable_sheet = lainuri.printer.get_sheet_check_in(event.items)
      lainuri.printer.print_html(printable_sheet)
      lainuri.event_queue.push_event(
        le.LEPrintResponse(
          receipt_type=event.receipt_type, items=event.items, user_barcode=event.user_barcode, printable_sheet=printable_sheet,
          status=Status.SUCCESS,
        )
      )
  except Exception as e:
    lainuri.event_queue.push_event(
      le.LEPrintResponse(
        receipt_type=event.receipt_type, items=event.items, user_barcode=event.user_barcode, printable_sheet=printable_sheet or None,
        status=Status.ERROR,
        states={
          'exception': {
            'type': type(e).__name__,
            'trace': traceback.format_exc(),
          },
        }
      )
    )
