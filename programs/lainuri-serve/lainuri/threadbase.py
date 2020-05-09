from lainuri.config import get_config
from lainuri.logging_context import logging
log = logging.getLogger(__name__)

import threading
import time

class Threadbase(threading.Thread):

  def __init__(self, name: str, worker_method: callable, listen_for_event: bool = False):
    threading.Thread.__init__(self, name=name)
    self.worker_method = worker_method
    self.killswitch = None
    self.listen_for_event = listen_for_event
    self.threading_event = None
    self.threading_event_data = None
    if self.listen_for_event:
      self.threading_event = threading.Event()

  def kill(self):
    self.killswitch = 'engage'

  def notify(self, data: any = None):
    if not self.threading_event: raise TypeError(f"Thread '{self.name}' is not initialized with listen_for_event=True. So threading event listening is not active.")
    self.threading_event.set()
    self.threading_event_data = data

  def run(self):
    log.info(f"Thread '{self.name}' starting")
    while(threading.main_thread().is_alive()):
      if self.killswitch:
        self.killswitch = None
        break
      if self.listen_for_event:
        if not self.threading_event.wait(1):
          continue
        else:
          self.threading_event.clear()
      try:
        m = getattr(self, 'worker_method')
        if self.threading_event_data: m(self.threading_event_data)
        else: m()
      except Exception as e:
        log.exception(f"Exception {type(e)} at thread '{self.name}'")
        time.sleep(0.5)

    log.info(f"Thread '{self.name}' terminating")
