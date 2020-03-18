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
      receipt_template = get_config('devices.thermal-printer.check-out-receipt')

      borrower = koha_api.get_borrower(event.user_barcode)

      printable_sheet = None
      if receipt_template.lower() == 'koha':
        printable_sheet = koha_api.receipt(borrower['borrowernumber'], 'qslip', event.locale)
      else:
        printable_sheet = lainuri.printer.get_sheet(receipt_template, event.items, borrower)

      lainuri.printer.print_html(printable_sheet)
      lainuri.event_queue.push_event(
        le.LEPrintResponse(
          receipt_type=event.receipt_type, items=event.items, user_barcode=event.user_barcode, printable_sheet=printable_sheet, locale=event.locale,
          status=Status.SUCCESS,
        )
      )

    elif event.receipt_type == 'check-in':
      receipt_template = get_config('devices.thermal-printer.check-in-receipt')

      if event.user_barcode: borrower = koha_api.get_borrower(event.user_barcode)

      printable_sheet = None
      if receipt_template.lower() == 'koha':
        if not borrower: raise TypeError("config('devices.thermal-printer.check-in-receipt') cannot be 'koha', because no way of telling Koha which user did the returns without forcing login.")
        printable_sheet = koha_api.receipt(borrower['borrowernumber'], 'checkinslip', event.locale)
      else:
        printable_sheet = lainuri.printer.get_sheet(receipt_template, event.items, {})

      lainuri.printer.print_html(printable_sheet)
      lainuri.event_queue.push_event(
        le.LEPrintResponse(
          receipt_type=event.receipt_type, items=event.items, user_barcode=event.user_barcode, printable_sheet=printable_sheet, locale=event.locale,
          status=Status.SUCCESS,
        )
      )
  except Exception as e:
    lainuri.event_queue.push_event(
      le.LEPrintResponse(
        receipt_type=event.receipt_type, items=event.items, user_barcode=event.user_barcode, printable_sheet=printable_sheet or None, locale=event.locale,
        status=Status.ERROR,
        states={
          'exception': {
            'type': type(e).__name__,
            'trace': traceback.format_exc(),
          },
        }
      )
    )
