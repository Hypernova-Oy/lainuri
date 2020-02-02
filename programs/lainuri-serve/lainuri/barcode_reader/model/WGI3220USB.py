from lainuri.config import get_config
from lainuri.logging_context import logging
log = logging.getLogger(__name__)

import serial

import lainuri.helpers
from lainuri.barcode_reader.model.WGC_commands import *


def connect(self):
  port = lainuri.helpers.find_dev_path('24EA', '0197')
  log.info(f"Connecting to port='{port}'")
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
