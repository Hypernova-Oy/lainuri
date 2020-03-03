from lainuri.config import get_config
from lainuri.logging_context import logging
log = logging.getLogger(__name__)

import subprocess
import traceback

import lainuri.event as le
import lainuri.event_queue
from lainuri.koha_api import koha_api
import lainuri.printer

def print_receipt(event):
  if event.receipt_type == 'check-out':
    return print_check_out_receipt(event)
  elif event.receipt_type == 'check-in':
    return print_check_in_receipt(event)

def print_check_out_receipt(event):
  try:
    borrower = koha_api.get_borrower(event.user_barcode)
    printable_sheet = koha_api.receipt(borrower['borrowernumber'])
    import pdb; pdb.set_trace()
    lainuri.printer.print_html(printable_sheet)
    lainuri.event_queue.push_event(
      le.LEPrintResponse(event.receipt_type, event.items, event.user_barcode, printable_sheet, {
        'success': 'ok'
      })
    )
  except subprocess.CalledProcessError as e:
    lainuri.event_queue.push_event(
      le.LEPrintResponse(event.receipt_type, event.items, event.user_barcode, printable_sheet, {
        'exception': traceback.format_exc() + ". exit='" + e.returncode + "' output='" + e.output + "'"
      })
    )
  except subprocess.TimeoutExpired as e:
    lainuri.event_queue.push_event(
      le.LEPrintResponse(event.receipt_type, event.items, event.user_barcode, printable_sheet, {
        'exception': traceback.format_exc() + ". output='" + e.output + "'"
      })
    )
  except Exception as e:
    lainuri.event_queue.push_event(
      le.LEPrintResponse(event.receipt_type, event.items, event.user_barcode, '', {
        'exception': traceback.format_exc()
      })
    )

def print_check_in_receipt(event):
  try:
    printable_sheet = lainuri.printer.get_sheet_check_in(event.items)
    lainuri.printer.print_html(printable_sheet)
    lainuri.event_queue.push_event(
      le.LEPrintResponse(event.receipt_type, event.items, event.user_barcode, printable_sheet, {
        'success': 'ok'
      })
    )
  except subprocess.CalledProcessError as e:
    lainuri.event_queue.push_event(
      le.LEPrintResponse(event.receipt_type, event.items, event.user_barcode, printable_sheet, {
        'exception': traceback.format_exc() + ". exit='" + e.returncode + "' output='" + e.output + "'"
      })
    )
  except subprocess.TimeoutExpired as e:
    lainuri.event_queue.push_event(
      le.LEPrintResponse(event.receipt_type, event.items, event.user_barcode, printable_sheet, {
        'exception': traceback.format_exc() + ". output='" + e.output + "'"
      })
    )
  except Exception as e:
    lainuri.event_queue.push_event(
      le.LEPrintResponse(event.receipt_type, event.items, event.user_barcode, '', {
        'exception': traceback.format_exc()
      })
    )
