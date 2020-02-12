#!/usr/bin/python3
"""
Simple manual test program to test the barcode reader
"""

from lainuri.config import c
from lainuri.logging_context import logging
log = logging.getLogger(__name__)

import time

from lainuri.barcode_reader import BarcodeReader
from lainuri.barcode_reader.model.WGI_commands import *

#c['devices']['barcode-reader']['model'] = 'WGI3220USB'

bcr = BarcodeReader()

"""
bcr.write(WGI_ACKFeedback())
time.sleep(0.1)
print(bcr.read())

bcr.write(WGI_ReadVersion())
time.sleep(0.1)
print(bcr.read())

bcr.write(WGI_ConfirmCommunicationStatus())
time.sleep(0.1)
print(bcr.read())

bcr.write(WGI_TurnOn1DCode())
time.sleep(0.1)
print(bcr.read())

bcr.write(WGI_ScanMode(auto_scan=1))
time.sleep(1)
print(bcr.read())
"""

print("READ READ READ")
print(bcr.blocking_read())
