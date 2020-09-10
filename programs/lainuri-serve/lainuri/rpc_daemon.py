from lainuri.config import get_config
from lainuri.logging_context import logging
log = logging.getLogger(__name__)

import lainuri.websocket_server

import pathlib
import rpyc
from rpyc.core import SlaveService
from rpyc.utils.server import ThreadedServer # or ForkingServer
import threading


server = None
daemon = None

class VirtualBarcodeService(rpyc.Service):
  def exposed_read_virtual_barcode(self, barcode): # this is an exposed method
    lainuri.websocket_server.handle_barcode_read(None, barcode)

def _start_rpyc_server():
  global server
  try:
    if get_config('server.rpc-daemon.service-impl') == "SlaveService":          server = ThreadedServer(SlaveService, socket_path='lainuri_rpc.sock')
    if get_config('server.rpc-daemon.service-impl') == "VirtualBarcodeService": server = ThreadedServer(VirtualBarcodeService, hostname="localhost", port=59998) # Modern service client doesn't support unix domain sockets with custom service
    server.start()
  except Exception as e:
    log.exception(e)
  finally:
    if get_config('server.rpc-daemon.service-impl') == "SlaveService": pathlib.Path('lainuri_rpc.sock').unlink()

def get_daemon():
  global daemon
  return daemon

def start_daemon():
  global daemon
  if not get_config('server.rpc-daemon.enabled'):
    return daemon
  daemon = threading.Thread(target=_start_rpyc_server)
  daemon.start()
  return daemon

def stop_daemon():
  global daemon
  if not daemon: return daemon
  server.close()
  return daemon
