from lainuri.config import get_config
from lainuri.logging_context import logging
log = logging.getLogger(__name__)

from lainuri.constants import Status
import lainuri.event
import lainuri.event_queue

import _thread as thread
import threading
import traceback

event_play_ringtone = threading.Event()
play_ringtone_event = None

def play_rtttl(ringtone_name: str, rtttl_tunes: str):
  log.info(f"Playing rtttl '{ringtone}' '{rtttl_tunes}'")

  if get_config('devices.ringtone-player.enabled'):
    process = subprocess.Popen(['rtttl-player', '-o', 'random'], stdout=subprocess.PIPE, stdin=subprocess.PIPE, stderr=subprocess.PIPE)
    log.info("Stopped playing rtttl")
    if process.returncode != 0:
      raise Exception(f"Failed to play rtttl! Command exit='{process.returncode}', stderr='{process.stderr}', stdout='{process.stdout}'")
  else:
    log.info("RTTTL-Player is disabled by config")

def rtttl_daemon():
  while(1):
    event_play_ringtone.wait()
    event_play_ringtone.clear()

    states = {}
    try:
      lainuri.rtttl_player.play_rtttl(lainuri.config.get_ringtone(
        ringtone_name=play_ringtone_event.message.ringtone_type,
        rtttl_tunes=play_ringtone_event.message.ringtone
      ))
      status = Status.SUCCESS
    except Exception as e:
      status = Status.ERROR
      states['exception'] = traceback.format_exc()

    lainuri.event_queue.push_event(lainuri.event.LERingtonePlayComplete(
      status=status,
      states=states,
      ringtone_type=play_ringtone_event.message.ringtone_type,
    ))

  log.info(f"Terminating RTTTL-Player thread")
  exit(0)

thread.start_new_thread(rtttl_daemon, ())
