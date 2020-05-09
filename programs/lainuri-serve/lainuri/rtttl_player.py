from lainuri.config import get_config
from lainuri.logging_context import logging
log = logging.getLogger(__name__)

from lainuri.constants import Status
import lainuri.event
import lainuri.event_queue
from lainuri.threadbase import Threadbase

import re
import subprocess
import threading
import traceback


ringtone_type_songname_parser = re.compile(r'^[a-zA-Z0-9 \-_]+$')
rtttl_validator_re = re.compile(r"""
  ^
  ([a-zA-Z0-9 -_]+)
  :
  (d=\d+)?,?
  (o=\d+)?,?
  (b=\d+)?
  :
  (\d{0,2}[a-zA-Z]\#?\.?\d{0,2},)* # Too bad Python3's regexes do not support nested capture groups, we cannot use named capture groups here.
  (\d{0,2}[a-zA-Z]\#?\.?\d{0,2})
  $
""", re.X)


def list_rtttl() -> dict:
  global rtttl_validator_re

  process = None
  cmd = ['rtttl-player','-o','list']
  try:
    process = subprocess.Popen(cmd, stdout=subprocess.PIPE)
    process.wait(timeout=30)
    log.info("Listed rtttl")
    if process.returncode != 0:
      raise Exception("Process non-zero exit code")

    rtttls = {}
    for line in process.stdout:
      line = line.decode(encoding="utf-8", errors="strict")
      m = rtttl_validator_re.search(line)
      if m:
        rtttls[m.group(1)] = line

    return rtttls

  except Exception as e:
    raise type(e)(e, f"Failed to list rtttl! Command '{cmd}' exit='{process.returncode}', stderr='{process.stderr}', stdout='{process.stdout}'")


def play_rtttl(event: lainuri.event.LERingtonePlay):
  log.info(f"Playing rtttl '{event.ringtone}' '{event.ringtone_type}'")

  status = Status.NOT_SET
  states = {}

  try:
    if not get_config('devices.ringtone-player.enabled'):
      log.info("RTTTL-Player is disabled by config")
      states = {'exception': 'disabled by config'}
    else:
      _do_play(event)

    lainuri.event_queue.push_event(lainuri.event.LERingtonePlayComplete(
      ringtone_type=event.ringtone_type,
      ringtone=event.ringtone,
      status=Status.SUCCESS,
      states=states,
    ))

  except Exception as e:
    lainuri.event_queue.push_event(
      lainuri.event.LERingtonePlayComplete(
        ringtone_type=event.ringtone_type,
        ringtone=event.ringtone,
        status=Status.ERROR,
        states={
          'exception': {
            'type': type(e).__name__,
            'trace': traceback.format_exc(),
          },
        }
      )
    )

def _do_play(event: lainuri.event.LERingtonePlay):
  global ringtone_type_songname_parser, rtttl_validator_re

  ringtone = None
  if event.ringtone_type:
    ringtone = lainuri.config.get_ringtone(event.ringtone_type)
  else:
    ringtone = event.ringtone

  args = ['rtttl-player', '-o']

  if rtttl_validator_re.search(ringtone):
    args.append("--rtttl")
    args.append(ringtone)
    log.debug(f"Playing rtttl '{ringtone}'")
  elif ringtone_type_songname_parser.search(ringtone):
    args.append(f"song-{ringtone}")
    log.debug(f"Playing song '{ringtone}'")
  else:
    raise TypeError(f"ringtone '{ringtone}' is not a valid ringtone name or a rtttl-code")

  process = None
  try:
    process = subprocess.Popen(args)
    process.wait(timeout=120)
    log.info("Stopped playing rtttl")
    if process.returncode != 0:
      raise Exception("Process non-zero exit code")
  except Exception as e:
    raise type(e)(e, f"Failed to play rtttl! Command '{args}' exit='{process.returncode}', stderr='{process.stderr}', stdout='{process.stdout}'")

def rtttl_daemon(event: lainuri.event.LERingtonePlay):
    play_rtttl(event)

daemon = None
def get_player():
  global daemon
  if daemon: return daemon
  if get_config('devices.ringtone-player.enabled'):
    daemon = Threadbase(name='RTTTLPlayer', worker_method=rtttl_daemon, listen_for_event=True)
    return daemon
  else:
    log.info("RTTTL Player disabled by config")
