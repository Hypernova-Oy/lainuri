#!/usr/bin/python3

import context

import sys

from lainuri.WGCUsb300AT import BarcodeReader
from lainuri.WGCUsb300AT.model.WGC_commands import *

def test_barcode_reader():
  bcr = BarcodeReader()
  bcr.write(WGC_ScanTrigger())

  print("Manually read a barcode now:", file=sys.stderr)
  barcode = bcr.blocking_read()

  assert barcode
