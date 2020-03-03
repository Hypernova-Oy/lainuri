from lainuri.config import get_config
from lainuri.logging_context import logging
log = logging.getLogger(__name__)

import traceback

#from lainuri.event import LEvent # Cannot import this even for type safety, due to circular dependency

from lainuri.koha_api import koha_api
import lainuri.event
import lainuri.event_queue
import lainuri.rfid_reader as rfid


def checkout(event):
  try:
    # Get the borrower
    borrower = None
    try:
      borrower = koha_api.get_borrower(user_barcode=event.user_barcode)
    except Exception:
      lainuri.event_queue.push_event(
        lainuri.event.LECheckOutComplete(event.item_barcode, event.user_barcode, event.tag_type, 'failed', {
          'user_not_found': traceback.format_exc(),
        })
      )
      return

    # Get the itemnumber
    item = None
    try:
      item = koha_api.get_item(event.item_barcode)
    except Exception:
      lainuri.event_queue.push_event(
        lainuri.event.LECheckOutComplete(event.item_barcode, event.user_barcode, event.tag_type, 'failed', {
          'item_not_found': traceback.format_exc(),
        })
      )
      return

    # Get curated availability from the REST API. This doesn't say if the item could be checked out from this specific branch
    # but it is way better at communicating the small details.
    availability = koha_api.availability(itemnumber=item['itemnumber'], borrowernumber=borrower['borrowernumber'])
    if availability['available'] != True:
      lainuri.event_queue.push_event(
        lainuri.event.LECheckOutComplete(item['barcode'], borrower['cardnumber'], event.tag_type, 'failed', availability)
      )

    # Checkout to Koha
    (status, states) = koha_api.checkout(event.item_barcode, borrower['borrowernumber'])
    if status == 'failed':
      lainuri.event_queue.push_event(
        lainuri.event.LECheckOutComplete(event.item_barcode, borrower['cardnumber'], event.tag_type, 'failed', states)
      )
      return

    try:
      rfid.set_tag_gate_alarm(event, False)
    except Exception:
      states['set_tag_gate_alarm_failed'] = traceback.format_exc()
      lainuri.event_queue.push_event(
        lainuri.event.LECheckOutComplete(event.item_barcode, borrower['cardnumber'], event.tag_type, 'failed', states)
      )
      return

    # Send a notification to the UI
    lainuri.event_queue.push_event(
      lainuri.event.LECheckOutComplete(event.item_barcode, borrower['cardnumber'], event.tag_type, 'success', states)
    )

  except Exception:
    lainuri.event_queue.push_event(
      lainuri.event.LECheckOutComplete(event.item_barcode, borrower['cardnumber'], event.tag_type, 'failed', {
        'exception': traceback.format_exc(),
      })
    )
