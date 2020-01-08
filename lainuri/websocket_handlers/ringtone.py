from lainuri.event import LEvent

def ringtone_play(event: LEvent):
  import lainuri.rtttl_player # Device might be disabled so lazy load this on demand
  # Notify the RTTTL-Player thread that there is something to play.
  lainuri.rtttl_player.play_ringtone_event = event
  lainuri.rtttl_player.event_play_ringtone.set()
