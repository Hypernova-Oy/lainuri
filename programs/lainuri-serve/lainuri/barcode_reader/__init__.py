from lainuri.config import get_config
from lainuri.logging_context import logging
log = logging.getLogger(__name__)

import serial
import time
import _thread as thread
import threading
import traceback
import json
import importlib

import lainuri.helpers
import lainuri.barcode_reader.model.WGC300UsbAT as WGC300UsbAT
import lainuri.barcode_reader.model.WGI3220USB as WGI3220USB
from lainuri.threadbase import Threadbase


class BarcodeReader():
  def __init__(self, barcode_read_handler: callable=None):
    self.model = get_config('devices.barcode-reader.model')

    try:
      self.config_module = importlib.import_module(f'.{self.model}', 'lainuri.barcode_reader.model')
    except ModuleNotFoundError as e:
      raise Exception(f"Unknown barcode reader model '{self.model}'!")

    self.serial: serial.Serial = self.connect_serial()
    self.autoconfigure()

    self.barcode_read_handler = barcode_read_handler

  def connect_serial(self) -> serial.Serial:
    log.info(f"Connecting to '{self.model}'")
    return self.config_module.connect(self)

  def autoconfigure(self):
    log.info(f"Autoconfiguring '{self.model}'")
    self.config_module.autoconfigure(self)

  def is_connected(self):
    if not self.serial.is_open:
      log.error(f"Barcode reader serial connection lost! Reconnecting.")
      self.serial = connect(self)

  def send_command(self, command):
    """
    Send a command which is under the barcode reader device's communication protocol, checking for success or failure in message processing.
    """
    self.config_module.send_command(self, command)

  def write(self, cmd):
    """
    Write raw bytes to the serial connection
    """
    log.info(f"WRITE--> {type(cmd)}")
    data = cmd.pack()
    #for b in data: print(hex(b), ' ', end='')
    #print()
    rv = self.serial.write(data)
    log.info(f"-->WRITE {type(cmd)} '{rv}'")
    return rv

  def read(self):
    self.is_connected() # The serial connection can break during a long-running process, so reconnect if needed
    rv = b''
    self.serial.timeout = 0 # non-blocking mode, just read whatever is in the buffer
    while self.serial.in_waiting:
      rv = rv + self.serial.read(255)
    return rv

  def blocking_read(self, timeout: int = 3):
    """
    Use the serial-system's blocking read to notify us of new bytes to read, instead of looping and polling.
    If timeout happened, returns None
    Timeout is needed for the controlling thread to be able to receive commands.
    """
    self.serial.timeout = timeout
    rv = self.serial.read(1)
    if not rv: return None
    rv = rv + self.read()
    if (rv):
      log.debug(f"Received bytes='{rv.hex()}'")
    return rv

  def read_barcode_blocking(self):
    rv = self.blocking_read()
    if (rv):
      barcode = rv[0:-1].decode('latin1') # Pop the last character, as it it the barcode termination character
      log.info(f"Received barcode='{barcode}' bytes='{rv}'")
      return barcode

  def start_polling_barcodes(self):
    self.daemon = Threadbase(name='BarcodeReader', worker_method=self.polling_barcodes_thread, listen_for_event=False)
    self.daemon.start()
    return self.daemon

  def stop_polling_barcodes(self):
    self.daemon.kill()
    return self.daemon

  def polling_barcodes_thread(self):
    barcode = self.read_barcode_blocking()
    if barcode:
      if self.barcode_read_handler: self.barcode_read_handler(self, barcode)
      else: log.warn(f"polling_barcodes_thread():> barcode_read_handler not in place. Don't know what to do with barcode '{barcode}'?")



barcode_reader_singleton = None
def init(barcode_read_handler: callable):
  global barcode_reader_singleton
  if barcode_reader_singleton: raise RuntimeError("BarcodeReader daemon already initialized!")
  if get_config('devices.barcode-reader.enabled'):
    barcode_reader_singleton = BarcodeReader(barcode_read_handler=barcode_read_handler)
  else:
    log.info("Barcode reader disabled by config")
  return barcode_reader_singleton

def get_BarcodeReader():
  global barcode_reader_singleton
  if not barcode_reader_singleton: raise RuntimeError("BarcodeReader daemon not initialized yet!")
  return barcode_reader_singleton
