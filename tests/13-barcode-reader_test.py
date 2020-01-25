#!/usr/bin/python3

import context

import sys

from lainuri.barcode_reader import BarcodeReader
from lainuri.barcode_reader.model.WGC_commands import *

def test_barcode_reader():
  bcr = BarcodeReader()
  bcr.write(WGC_ScanTrigger())

  print("Manually read a barcode now:", file=sys.stderr)
  barcode = bcr.blocking_read()

  assert barcode
