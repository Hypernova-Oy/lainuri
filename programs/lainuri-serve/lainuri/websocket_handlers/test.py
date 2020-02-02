from lainuri.config import get_config
from lainuri.logging_context import logging
log = logging.getLogger(__name__)

import time

import lainuri.websocket_server
import lainuri.event
from lainuri.RL866.tag import Tag

def mock_devices(event):
  lainuri.websocket_server.push_event(lainuri.event.LERFIDTagsPresent([
    Tag(serial_number='0xe00401003f3827a7'),
    Tag(serial_number='0xe00401003f382624'),
    Tag(serial_number='0xe00401003f3855FF'),
  ], recipient=event.client))

  time.sleep(1)

  lainuri.websocket_server.push_event(lainuri.event.LEBarcodeRead('167A0170177'))

  time.sleep(1)

  lainuri.websocket_server.push_event(lainuri.event.LERFIDTagsNew([
    Tag(serial_number='0xe00401003fFFFFFF'),
  ],[
    Tag(serial_number='0xe00401003fFFFFFF'),
    Tag(serial_number='0xe00401003f3827a7'),
    Tag(serial_number='0xe00401003f382624'),
    Tag(serial_number='0xe00401003f3855FF'),
  ], recipient=event.client))