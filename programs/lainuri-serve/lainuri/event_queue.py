"""
Detach lainuri.websocket_server from other subsystems.
Enable running tests with less coupling.

Enable controlling server concurrency load.
"""

from lainuri.config import get_config
from lainuri.logging_context import logging
log = logging.getLogger(__name__)

import json
import queue
from simple_websocket_server import WebSocket
import _thread as thread
import time

history_size = 1024

history_lock = thread.allocate_lock()
q = queue.Queue(maxsize=0) # queue with infinite size
history = [None]*history_size # Persist event history here for complex problem debugging.
hii = 0

def push_event(event):
  global q
  event.serialized = event.serialize_ws()
  q.put(event)
  push_history(event)
  return event

def pop_event(timeout: int = None):
  global q
  return q.get(timeout=timeout)

def push_history(event):
  global history, hii, history_lock
  with history_lock:
    history[hii] = event
    hii += 1
    if hii >= history_size:
      history = history[-1*int(history_size/2):] + [None]*int(history_size/2)
      hii = int(history_size/2)
      log.info(f"event_queue history flushed")

def flush_all():
  """
  This is normally not needed. History automatically cleans itself.
  Used by testing to reset history state.
  """
  global history, hii, history_lock, q
  with history_lock:
    history = [None]*history_size
    hii = 0
  q = queue.Queue(maxsize=0)
  return True
