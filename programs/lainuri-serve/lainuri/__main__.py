from lainuri.config import get_config
from lainuri.logging_context import logging
log = logging.getLogger(__name__)

from pprint import pprint
import time

def handle_signal_SIGUSR1(signum, frame):
  import lainuri.event_queue
  print(f"Received signal SIGUSR1 '{signum}' '{frame}'")
  start = lainuri.event_queue.hii - 10 if lainuri.event_queue.hii - 10 > 0 else 0
  pprint([e.__dict__ for e in lainuri.event_queue.history[start:start+10] if e != None])


if __name__ == '__main__':
  import signal
  log.info("Binding signal handlers, SIGUSR1")
  signal.signal(signal.SIGUSR1, handle_signal_SIGUSR1)

  import lainuri.websocket_server
  lainuri.websocket_server.start(ws_daemon=False)
