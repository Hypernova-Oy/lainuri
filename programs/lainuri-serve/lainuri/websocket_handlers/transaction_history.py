from lainuri.config import get_config
from lainuri.logging_context import logging
log = logging.getLogger(__name__)

import traceback

import lainuri.db.transaction_history
import lainuri.event
import lainuri.event_queue
from lainuri.status import Status

def list_some(event):
  try:
    lainuri.event_queue.push_event(
      lainuri.event.LETransactionHistoryResponse(
        transactions=lainuri.db.transaction_history.list_between(transaction_date_start=event.start_time, transaction_date_end=event.end_time),
        status=Status.SUCCESS,
        states={},
      )
    )
  except Exception as e:
    lainuri.event_queue.push_event(
      lainuri.event.LETransactionHistoryResponse(
        transactions=[],
        status=Status.ERROR,
        states={'exception': {
          'type': type(e).__name__,
          'trace': str(e)}
        },
      )
    )
