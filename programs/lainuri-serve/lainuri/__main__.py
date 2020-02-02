from lainuri.config import get_config
from lainuri.logging_context import logging
log = logging.getLogger(__name__)

if __name__ == '__main__':
  import lainuri.websocket_server
  lainuri.websocket_server.start()
