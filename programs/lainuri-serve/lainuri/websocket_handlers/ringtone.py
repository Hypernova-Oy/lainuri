from lainuri.config import get_config
from lainuri.logging_context import logging
log = logging.getLogger(__name__)

import lainuri.rtttl_player

#from lainuri.event import LEvent # Cannot import this even for type safety, due to circular dependency

def ringtone_play(event):
  """
  Asynchronously dispatches a play notification to the rtttl-thread.
  The thread dispatches ringtone-play-complete -events.
  """
  # Notify the RTTTL-Player thread that there is something to play.
  lainuri.rtttl_player.play_ringtone_event = event
  lainuri.rtttl_player.event_play_ringtone.set()
