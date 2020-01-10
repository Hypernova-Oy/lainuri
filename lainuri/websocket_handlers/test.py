from lainuri.config import get_config
from lainuri.logging_context import logging
log = logging.getLogger(__name__)

import time

from lainuri.event import LEvent, LERFIDTagsNew, LERFIDTagsPresent, LEBarcodeRead
import lainuri.websocket_server
from lainuri.RL866.tag import Tag

def mock_devices(event: LEvent):
  lainuri.websocket_server.push_event(LERFIDTagsPresent([
    Tag(serial_number='0xe00401003f3827a7'),
    Tag(serial_number='0xe00401003f382624'),
    Tag(serial_number='0xe00401003f3855FF'),
  ], recipient=event.client))

  time.sleep(1)

  lainuri.websocket_server.push_event(LEBarcodeRead('167A0170177'))

  time.sleep(1)

  lainuri.websocket_server.push_event(LERFIDTagsNew([
    Tag(serial_number='0xe00401003fFFFFFF'),
  ],[
    Tag(serial_number='0xe00401003fFFFFFF'),
    Tag(serial_number='0xe00401003f3827a7'),
    Tag(serial_number='0xe00401003f382624'),
    Tag(serial_number='0xe00401003f3855FF'),
  ], recipient=event.client))
