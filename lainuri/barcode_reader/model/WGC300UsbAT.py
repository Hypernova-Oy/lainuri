from lainuri.config import get_config
from lainuri.logging_context import logging
log = logging.getLogger(__name__)

import serial
import time

import lainuri.helpers
from lainuri.barcode_reader.model.WGC_commands import *


def connect(self):
  port = lainuri.helpers.find_dev_path('8888', '0007')
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
    WGC_SettingsEnter(),
    WGC_AllBarcodes(disable_all_barcodes=1),
    WGC_Code39Enable(),
    WGC_Code39MinBarcodeLength(min_barcode_length=10),
    WGC_Code39MaxBarcodeLength(max_barcode_length=12),
    WGC_BarcodesSetSuffix(carriage_return_suffix=1), # TODO: The device actually doesn't set this new suffix, but it should set a suffix for better transport reliability.
    WGC_SettingsExit(),
  ]
  log.debug(f"Autoconfiguring '{[type(t) for t in configurations]}'")
  for cmd in configurations:
    self.write(cmd)
    time.sleep(0.05) # Wait a bit to let the barcode reader to digest the configuration directives

  time.sleep(1) # The barcode reader needs a second to reconfigure and be responsive again.

  self.write(WGC_VersionRead())
  version = self.read()
  log.info(f"Autoconfigured WGC300UsbAT version '{version}'\n{self.serial.__dict__}")
