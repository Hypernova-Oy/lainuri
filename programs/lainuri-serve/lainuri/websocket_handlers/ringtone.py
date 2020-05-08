from lainuri.config import get_config
from lainuri.logging_context import logging
log = logging.getLogger(__name__)

import lainuri.event
import lainuri.rtttl_player
from lainuri.constants import Status

import traceback


def ringtone_play(event: lainuri.event.LERingtonePlay):
  """
  Asynchronously dispatches a play notification to the rtttl-thread.
  The thread dispatches ringtone-play-complete -events.
  """
  # Notify the RTTTL-Player thread that there is something to play.
  lainuri.rtttl_player.play_ringtone_event = event
  lainuri.rtttl_player.event_play_ringtone.set()

def ringtone_list(event: lainuri.event.LERingtoneList = None):
  try:
    rtttls = lainuri.rtttl_player.list_rtttl()

    lainuri.event_queue.push_event(
      lainuri.event.LERingtoneListResponse(
        rtttls=rtttls,
        status=Status.SUCCESS,
        states={},
      )
    )
  except Exception as e:
    log.exception(f"Exception at {__name__}")
    lainuri.event_queue.push_event(
      lainuri.event.LERingtoneListResponse(
        rtttls={},
        status=Status.ERROR,
        states={'exception': {
          'type': type(e).__name__,
          'trace': str(e)}
        },
      )
    )
