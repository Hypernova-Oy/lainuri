#!/usr/bin/python3

import importlib

import context

from lainuri.config import get_config

import lainuri.helpers

def test_find_dev_path():
  model = get_config('devices.barcode-reader.model')
  config_module = importlib.import_module(f'.{model}', 'lainuri.barcode_reader.model')
  path = lainuri.helpers.find_dev_path(usb_vendor=config_module.usb_vendor, usb_model=config_module.usb_product)
  assert path
