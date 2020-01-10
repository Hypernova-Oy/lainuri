from lainuri.config import get_config
from lainuri.logging_context import logging
log = logging.getLogger(__name__)

import serial
import time
import _thread as thread
import json

import lainuri.helpers
from lainuri.WGCUsb300AT.commands import *

from lainuri.event import LEvent
import lainuri.websocket_server

class BarcodeReader():
  def __init__(self):
    self.serial: serial.Serial = self.connect_serial()
    self.autoconfigure()

  def connect_serial(self) -> serial.Serial:
    port = lainuri.helpers.find_dev_path('8888', '0007');
    log.info(f"Connecting WGC300 to port='{port}'")
    ser = serial.Serial()
    ser.baudrate = 115200
    ser.parity = serial.PARITY_NONE
    ser.databits = 8
    ser.stopbits = 1
    ser.port = port
    ser.timeout = 0
    ser.open()
    return ser

  def autoconfigure(self):
    log.info("Autoconfiguring WGC300")
    configurations = [
      WGC_SettingsEnter(),
      WGC_AllBarcodes(disable_all_barcodes=1),
      WGC_Code39Enable(),
      WGC_Code39MinBarcodeLength(min_barcode_length=10),
      WGC_Code39MaxBarcodeLength(max_barcode_length=12),
      WGC_BarcodesSetSuffix(carriage_return_suffix=1), # TODO: The device actually doesn't set this new suffix, but it should set a suffix for better transport reliability.
      WGC_SettingsExit(),
    ]
    for cmd in configurations:
      self.write(cmd)

  def write(self, cmd: WGCCommand):
    log.info(f"WRITE--> {type(cmd)}")
    data = cmd.pack()
    for b in data: print(hex(b), ' ', end='')
    print()
    rv = self.serial.write(data)
    log.info(f"-->WRITE {type(cmd)}")
    return rv

  def read(self):
    timeout = 5
    log.info(f"READ WAITING-->")
    slept = 0
    self.serial.timeout(0) # non-blocking mode, return immediately in any case, returning zero or more, up to the requested number of bytes
    while(self.serial.in_waiting == 0):
      time.sleep(0.1)
      slept += 0.1
      if slept > timeout:
        raise Exception("read timeout")

    rv_a = bytearray()
    while self.serial.in_waiting:
      log.info(f"READ-->")
      #rv = ser.read(255)
      rv = self.serial.readline()
      rv_a += rv
      time.sleep(0.1)
    for b in rv_a: print(hex(b), ' ', end='')
    print()
    log.info(f"-->READ")
    return rv_a

  def start_polling_barcodes(self):
    """
    Forks a thread to poll the serial connection for barcodes.
    Turns the read barcodes into push notifications.
    """
    if get_config('devices.barcode-reader.enabled'):
      thread.start_new_thread(self.polling_barcodes_thread, ())
    else:
      log.info("WGC300 reader is disabled by config")

  def polling_barcodes_thread(self):
    log.info("Barcodes polling starting")

    while(1):
      # Use the serial-system's blocking read to notify us of new bytes to read, instead of looping and polling.
      self.serial.timeout = None # wait forever / until requested number of bytes are received
      rv = self.serial.read(1)
      self.serial.timeout = 0 # non-blocking mode, just read whatever is in the buffer
      while self.serial.in_waiting:
        rv = rv + self.serial.read(255)

      if (rv):
        log.info(f"Received barcode '{rv}'")
        lainuri.websocket_server.push_event(LEvent("barcode-read", {
          'barcode': rv,
        }))

    log.info(f"Terminating WGC300 thread")
