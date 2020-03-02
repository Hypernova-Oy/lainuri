from lainuri.config import get_config
from lainuri.logging_context import logging
log = logging.getLogger(__name__)

import serial
import time

import lainuri.helpers
from lainuri.barcode_reader.model.WGI_commands import *

usb_vendor = '24EA'
usb_model = '0187'

def connect(self):
  port = lainuri.helpers.find_dev_path(usb_vendor, usb_model)
  log.info(f"Connecting to port='{port}'")
  ser = serial.Serial()
  ser.baudrate = 9600
  ser.parity = serial.PARITY_NONE
  ser.databits = 8
  ser.stopbits = 1
  ser.port = port
  ser.timeout = 0
  ser.open()
  return ser

def autoconfigure(self):
  configurations = [
    WGI_RestoreDefault(),
    WGI_ConfirmCommunicationStatus(),
    WGI_ScanMode(auto_scan=1),
    WGI_AimingLight(always_on=1),
    WGI_IlluminateWorkMode(always_on=1),
    WGI_TurnOnAllCode(),
  ]
  for cmd in configurations:
    send_command(self, cmd)
    time.sleep(0.1)

def send_command(self, cmd):
  self.write(cmd)
  byttes = self.blocking_read()
  if not (byttes and byttes == b'\x52\xA0\xEC\xFE\x74'):
    raise Exception(f"Sending command {cmd} failed due to device error response.")

