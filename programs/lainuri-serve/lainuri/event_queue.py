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

history_lock = thread.allocate_lock()
q = queue.Queue(maxsize=0) # queue with infinite size
history = [None]*1024 # Persist event history here for complex problem debugging.
hii = 0

def push_event(event):
  global q
  q.put(event)
  push_history(event)
  return event

def pop_event():
  global q
  return q.get()

def push_history(event):
  global history, hii, history_lock
  with history_lock:
    history[hii] = event
    hii += 1
    if hii >= 1024:
      history = history[-512:] + [None]*512
      hii = 512
      log.info(f"event_queue history flushed")

