#!/usr/bin/python3

import context

import lainuri.helpers

def test_find_dev_path():
  """
  Looks for the WGC300UsbAT -device
  """
  path = lainuri.helpers.find_dev_path(usb_vendor='8888', usb_model='0007')
  assert path
