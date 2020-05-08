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


class BarcodeReader():
  def __init__(self):
    self.model = get_config('devices.barcode-reader.model')
    self.barcode_polling_thread_stop_polling = False

    try:
      self.config_module = importlib.import_module(f'.{self.model}', 'lainuri.barcode_reader.model')
    except ModuleNotFoundError as e:
      raise Exception(f"Unknown barcode reader model '{self.model}'!")

    self.serial: serial.Serial = self.connect_serial()
    self.autoconfigure()

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
    for b in data: print(hex(b), ' ', end='')
    print()
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

  def blocking_read(self):
    """
    Use the serial-system's blocking read to notify us of new bytes to read, instead of looping and polling.
    """
    self.serial.timeout = None # wait forever / until requested number of bytes are received
    rv = self.serial.read(1)
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

  def start_polling_barcodes(self, handler):
    """
    Forks a thread to poll the serial connection for barcodes.
    Turns the read barcodes into push notifications.
    """
    self.barcode_polling_thread_stop_polling = False
    self.barcode_polling_thread = threading.Thread(name="barcode_polling_thread", target=self.polling_barcodes_thread, args=(handler, True))
    self.barcode_polling_thread.start()
    return self.barcode_polling_thread

  def stop_polling_barcodes(self):
    """
    Stops only after one more barcode is read
    """
    self.barcode_polling_thread_stop_polling = True

  def polling_barcodes_thread(self, handler, dummy):
    log.info("Barcodes polling starting")

    while(threading.main_thread().is_alive()):
      if self.barcode_polling_thread_stop_polling == True:
        self.barcode_polling_thread_stop_polling = False
        break

      try:
        barcode = self.read_barcode_blocking()
        if (barcode):
          handler(barcode)
      except Exception as e:
        log.error(f"Polling barcodes received an exception='{type(e)}'\n{traceback.format_exc()}") # The prefix text is used to find caught exceptions!

    log.info(f"Terminating barcode polling thread")

barcode_reader_singleton = None
def get_BarcodeReader() -> BarcodeReader:
  global barcode_reader_singleton
  if not barcode_reader_singleton: barcode_reader_singleton = BarcodeReader()
  return barcode_reader_singleton
