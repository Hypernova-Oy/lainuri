from lainuri.config import get_config
from lainuri.logging_context import logging
log = logging.getLogger(__name__)

#from lainuri.event import LEvent # Cannot import this even for type safety, due to circular dependency

def ringtone_play(event):
  get_config('devices.ringtone-player.enabled')
  if get_config('devices.ringtone-player.enabled'):
    import lainuri.rtttl_player # Device might be disabled so lazy load this on demand
    # Notify the RTTTL-Player thread that there is something to play.
    lainuri.rtttl_player.play_ringtone_event = event
    lainuri.rtttl_player.event_play_ringtone.set()
  else:
    log.info("RTTTL-Player is disabled by config")
