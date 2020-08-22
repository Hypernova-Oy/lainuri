from lainuri.config import get_config
from lainuri.logging_context import logging
log = logging.getLogger(__name__)

import json
import subprocess
import traceback

from lainuri.constants import Status
import lainuri.event as le
import lainuri.event_queue
from lainuri.koha_api import koha_api
import lainuri.printer
from lainuri.printer.printjob import PrintJob

def list_templates(event: le.LEPrintTemplateList):
  try:
    lainuri.event_queue.push_event(
      le.LEPrintTemplateListResponse(
        templates=lainuri.printer.list_templates(),
        status=Status.SUCCESS,
      )
    )

  except Exception as e:
    log.exception(f"Exception during list_templates")
    lainuri.event_queue.push_event(
      le.LEPrintTemplateListResponse(
        templates={},
        status=Status.ERROR,
        states={'exception': {
          'type': type(e).__name__,
          'trace': str(e)}
        },
      )
    )

def test_print(event: le.LEPrintTestRequest):
  pj = None

  try:
    pj = PrintJob('test', data=json.loads(event.data))
    pj.css = event.css
    pj._receipt_template = event.template
    pj = lainuri.printer.test_print(pj, real_print=event.real_print)

    lainuri.event_queue.push_event(
      le.LEPrintTestResponse(
        image=pj._png_file_path.read_bytes(),
        status=Status.SUCCESS,
      )
    )

  except Exception as e:
    log.exception(f"Exception with PrintJob={pj.__dict__}")
    lainuri.event_queue.push_event(
      le.LEPrintTestResponse(
        image=bytes(),
        status=Status.ERROR,
        states={'exception': {
          'type': type(e).__name__,
          'trace': str(e)}
        },
      )
    )
  return pj

def print_receipt(event):
  pj = None

  try:
    if event.receipt_type == 'check-out':
      pj = PrintJob('checkout', {"items": event.items, "user": koha_api.get_borrower(event.user_barcode)})
      pj = lainuri.printer.print_check_out_receipt(pj)
    elif event.receipt_type == 'check-in':
      pj = PrintJob('checkin', {"items": event.items, "user": {}})
      pj = lainuri.printer.print_check_in_receipt(pj)
    else:
      raise ValueError(f"print_receipt() Unknown receipt_type '{event.receipt_type}'!")

    lainuri.event_queue.push_event(
      le.LEPrintResponse(
        receipt_type=event.receipt_type, items=event.items, user_barcode=event.user_barcode, printable_sheet=pj._printable_html,
        status=Status.SUCCESS, # We are waiting for the end-user to tear off the receipt, see lainuri.printer.status
      )
    )

    #lainuri.printer.status.start_polling_for_receipt_torn(event)

  except Exception as e:
    log.exception(f"Exception with PrintJob={pj.__dict__}")
    lainuri.event_queue.push_event(
      le.LEPrintResponse(
        receipt_type=event.receipt_type, items=event.items, user_barcode=event.user_barcode, printable_sheet=pj._printable_html or None,
        status=Status.ERROR,
        states={'exception': {
          'type': type(e).__name__,
          'trace': str(e)}
        },
      )
    )
  return pj

def save_template(event):
  try:
    lainuri.printer.save_template(event)

    lainuri.event_queue.push_event(
      le.LEPrintTemplateSaveResponse(
        id=event.id,
        type=event.type,
        locale_code=event.locale_code,
        status=Status.SUCCESS,
      )
    )

  except Exception as e:
    log.exception(f"Exception saving template")
    lainuri.event_queue.push_event(
      le.LEPrintTemplateSaveResponse(
        id=None,
        type=event.type,
        locale_code=event.locale_code,
        status=Status.ERROR,
        states={'exception': {
          'type': type(e).__name__,
          'trace': str(e)}
        },
      )
    )
