#!/usr/bin/python3

import context
from lainuri.config import get_config

import time
import pytest_subtests

import lainuri.websocket_server
import lainuri.event as le
import lainuri.websocket_handlers.checkin
import lainuri.websocket_handlers.checkout
import lainuri.rfid_reader as rfid


good_item_barcode = '1620154429'
good_user_barcode = '23529000035676'

def test_checkout_barcode(subtests):
  global good_item_barcode, good_user_barcode
  borrower = None

  with subtests.test("When the barcode is checked in"):
    event = le.LECheckIn(item_barcode=good_item_barcode, tag_type='barcode')
    lainuri.websocket_handlers.checkin.checkin(event)

  with subtests.test("Then a response event in generated"):
    event = lainuri.event_queue.history[0]
    assert type(event) == le.LECheckInComplete
    assert event.item_barcode == good_item_barcode
    assert event.status == 'complete'

  with subtests.test("When the barcode is checked out"):
    event = le.LECheckOut(item_barcode=good_item_barcode, user_barcode=good_user_barcode, tag_type='barcode')
    lainuri.websocket_handlers.checkout.checkout(event)

  with subtests.test("Then the LECheckOutComplete-event has the expected contents"):
    event = lainuri.event_queue.history[1]
    assert type(event) == le.LECheckOutComplete
    assert event.item_barcode == good_item_barcode
    assert event.status == 'complete'



def test_checkout_rfid(subtests):
  global good_item_barcode
  tag = None
  borrower = None
  event = None

  assert get_config('devices.rfid-reader.enabled') == True

  with subtests.test("Given a rfid reader which has RFID tags in reading radius"):
    rfid_reader = rfid.RFID_Reader()
    assert len(rfid_reader.do_inventory().tags_new) > 0

  with subtests.test("And a RFID tag"):
    tags_present = rfid.get_current_inventory_status()
    assert len(tags_present) > 0
    tag = tags_present[0]

  with subtests.test("And the RFID tag is registered in the test Koha instance as a circulable Item"):
    assert tag.iso25680_get_primary_item_identifier() == good_item_barcode

  with subtests.test("When the tag is checked in"):
    event = le.LECheckIn(item_barcode=tag.iso25680_get_primary_item_identifier(), tag_type='rfid')
    lainuri.websocket_handlers.checkin.checkin(event)

  with subtests.test("Then a response event in generated"):
    event = lainuri.event_queue.history[3]
    assert type(event) == le.LECheckInComplete
    assert event.status == 'complete'

  with subtests.test("And the gate security alarm is enabled"):
    assert tag.afi() == get_config('devices.rfid-reader.afi-checkin')

  with subtests.test("When the tag is checked out"):
    event = le.LECheckOut(item_barcode=tag.iso25680_get_primary_item_identifier(), user_barcode=good_user_barcode, tag_type='barcode')
    lainuri.websocket_handlers.checkout.checkout(event)

  with subtests.test("And the gate security alarm is disabled"):
    assert tag.afi() == get_config('devices.rfid-reader.afi-checkout')

  with subtests.test("Then a LECheckOutComplete-event is dispatched"):
    event = lainuri.event_queue.history[1]
    assert type(event) == le.LECheckOutComplete
    assert event.status == 'complete'

