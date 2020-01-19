from lainuri.config import get_config
from lainuri.logging_context import logging
log = logging.getLogger(__name__)

import subprocess
import traceback

import lainuri.event as le
from lainuri.koha_api import koha_api
import lainuri.websocket_server
import lainuri.printer

def print_receipt(event):
  try:
    borrower = koha_api.get_borrower(event.user_barcode)
    printable_sheet = koha_api.receipt(borrower['borrowernumber'])
    process = lainuri.printer.print_html(printable_sheet)
    lainuri.websocket_server.push_event(
      le.LEPrintResponse(event.items, event.user_barcode, printable_sheet, {
        'success': 'ok'
      })
    )
  except subprocess.CalledProcessError as e:
    lainuri.websocket_server.push_event(
      le.LEPrintResponse(event.items, event.user_barcode, printable_sheet, {
        'exception': traceback.format_exc() + ". exit='" + e.returncode + "' output='" + e.output + "'"
      })
    )
  except subprocess.TimeoutExpired as e:
    lainuri.websocket_server.push_event(
      le.LEPrintResponse(event.items, event.user_barcode, printable_sheet, {
        'exception': traceback.format_exc() + ". output='" + e.output + "'"
      })
    )
  except Exception as e:
    lainuri.websocket_server.push_event(
      le.LEPrintResponse(event.items, event.user_barcode, '', {
        'exception': traceback.format_exc()
      })
    )
