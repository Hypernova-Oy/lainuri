from lainuri.config import get_config
from lainuri.logging_context import logging
log = logging.getLogger(__name__)
log_external = logging.getLogger(__name__+'_external')

import time
import traceback

from lainuri.constants import Status
import lainuri.event
import lainuri.event_queue


def write_external_log(event: lainuri.event.LELogSend):
  try:
    for log_record in event.messages:
      log_external.log(
        logging.FATAL,
        time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(log_record['milliseconds']/1000)) +'.'+ str(log_record['milliseconds'] % 1000) + ' ' +
        '[' + log_record['level'] + '] ' +
        '(' + log_record['logger_name'] + ') ' +
        log_record['log_entry'],
      )
      # Logging responses are too expensive. Try to preserve UI responsiveness.
      #lainuri.event_queue.push_event(
      #  lainuri.event.LELogReceived(
      #    status=Status.SUCCESS,
      #    states={},
      #  )
      #)
  except Exception as e:
    log.exception(f"Exception at {__name__}")
    lainuri.event_queue.push_event(
      lainuri.event.LELogReceived(
        status=Status.ERROR,
        states={'exception': {
          'type': type(e).__name__,
          'trace': str(e)}
        },
      )
    )
