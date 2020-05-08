from lainuri.config import get_config
from lainuri.logging_context import logging
log = logging.getLogger(__name__)

import traceback

from lainuri.koha_api import koha_api
from lainuri.constants import Status
import lainuri.event
import lainuri.event_queue


def login_user(user_barcode: str):
  borrower = None
  try:
    borrower = koha_api.get_borrower(user_barcode=user_barcode)
    koha_api.authenticate_user(user_barcode=user_barcode)
    lainuri.event_queue.push_event(
      lainuri.event.LEUserLoginComplete(
        firstname=borrower['firstname'],
        surname=borrower['surname'],
        user_barcode=borrower['cardnumber'],
        status=Status.SUCCESS,
      )
    )
  except Exception as e:
    log.exception(f"Exception at {__name__}")
    lainuri.event_queue.push_event(
      lainuri.event.LEUserLoginComplete(
        firstname=borrower['firstname'] if borrower else '',
        surname=borrower['surname'] if borrower else '',
        user_barcode=borrower['cardnumber'] if borrower else user_barcode,
        status=Status.ERROR,
        states={'exception': {
          'type': type(e).__name__,
          'trace': str(e)}
        },
      )
    )
