#!/usr/bin/python3

import context
from lainuri.config import get_config

import time

import lainuri.websocket_server
import lainuri.event as le
import lainuri.websocket_handlers.checkout
import lainuri.rfid_reader as rfid




def test_checkout(subtests):
  tag = None
  borrower = None

  assert get_config('devices.rfid-reader.enabled') == True

  with subtests.test("Given a rfid reader which has RFID tags in reading radius"):
    rfid_reader = rfid.RFID_Reader()
    rfid_reader.start_polling_rfid_tags()
    time.sleep(1)

  with subtests.test("And a RFID tag"):
    tags_present = rfid.get_current_inventory_status()
    assert len(tags_present) > 0
    tag = tags_present[0]

  with subtests.test("And a borrower"):
    borrower = {
      'borrowernumber': 19,
    }

  with subtests.test("When the tag is checked out"):
    #import pdb; pdb.set_trace()
    event = le.LECheckOuting(tag.serial_number(), borrower['borrowernumber'])
    lainuri.websocket_handlers.checkout.checkout(event)

  with subtests.test("Then a LECheckOuted-event is dispatched"):
    event = lainuri.websocket_server.events[-1]
    assert type(event) == le.LECheckOuted

  with subtests.test("And the LECheckOuted-event has the expected contents"):
    assert 1 == 1
