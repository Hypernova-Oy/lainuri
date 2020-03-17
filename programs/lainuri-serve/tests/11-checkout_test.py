#!/usr/bin/python3

import context
from lainuri.config import get_config

import time
import pytest_subtests

import lainuri.websocket_server
import lainuri.koha_api
from lainuri.constants import Status
import lainuri.event as le
import lainuri.websocket_handlers.checkin
import lainuri.websocket_handlers.checkout
import lainuri.rfid_reader as rfid


good_item_barcode = '1620154429'
good_user_barcode = '23529000035676'

def test_checkout_barcode_via_event_queue(subtests):
  global good_item_barcode, good_user_barcode
  borrower = None
  assert lainuri.event_queue.flush_all()

  with subtests.test("Given an API authentication"):
    assert lainuri.koha_api.koha_api.authenticate()

  with subtests.test("When the barcode is checked in"):
    event = le.LECheckIn(item_barcode=good_item_barcode, tag_type='barcode')
    lainuri.event_queue.push_event(event)
    assert lainuri.websocket_server.handle_one_event(5) == event
    assert event == lainuri.event_queue.history[0]

  with subtests.test("Then a response event in generated"):
    event = lainuri.websocket_server.handle_one_event(5)
    assert event == lainuri.event_queue.history[1]
    assert type(event) == le.LECheckInComplete
    assert event.item_barcode == good_item_barcode
    assert event.status == Status.SUCCESS

  with subtests.test("When the barcode is checked out"):
    event = le.LECheckOut(item_barcode=good_item_barcode, user_barcode=good_user_barcode, tag_type='barcode')
    lainuri.event_queue.push_event(event)
    assert lainuri.websocket_server.handle_one_event(5) == event
    assert event == lainuri.event_queue.history[2]

  with subtests.test("Then the LECheckOutComplete-event has the expected contents"):
    event = lainuri.websocket_server.handle_one_event(5)
    assert event == lainuri.event_queue.history[3]
    assert type(event) == le.LECheckOutComplete
    assert event.item_barcode == good_item_barcode
    assert event.status == Status.SUCCESS



def test_checkout_rfid_via_event_queue(subtests):
  global good_item_barcode
  tag = None
  borrower = None
  event = None
  assert lainuri.event_queue.flush_all()

  assert get_config('devices.rfid-reader.enabled') == True

  with subtests.test("Given an API authentication"):
    assert lainuri.koha_api.koha_api.authenticate()

  with subtests.test("And a rfid reader which has RFID tags in reading radius"):
    rfid_reader = rfid.get_rfid_reader()
    assert len(rfid_reader.do_inventory().tags_present) > 0
    event = lainuri.websocket_server.handle_one_event(5)
    assert type(event) == lainuri.event.LERFIDTagsNew
    assert event == lainuri.event_queue.history[0]

  with subtests.test("And a RFID tag"):
    tags_present = rfid.get_current_inventory_status()
    assert len(tags_present) > 0
    tag = tags_present[0]

  with subtests.test("And the RFID tag is registered in the test Koha instance as a circulable Item"):
    assert tag.iso25680_get_primary_item_identifier() == good_item_barcode

  with subtests.test("When the tag is checked in"):
    event = le.LECheckIn(item_barcode=tag.iso25680_get_primary_item_identifier(), tag_type='rfid')
    lainuri.event_queue.push_event(event)
    assert lainuri.websocket_server.handle_one_event(5) == event
    assert event == lainuri.event_queue.history[1]

  with subtests.test("Then a response event is generated"):
    event = lainuri.websocket_server.handle_one_event(5)
    assert event == lainuri.event_queue.history[2]
    assert type(event) == le.LECheckInComplete
    assert event.status == Status.SUCCESS

  with subtests.test("When the tag is checked out"):
    event = le.LECheckOut(item_barcode=tag.iso25680_get_primary_item_identifier(), user_barcode=good_user_barcode, tag_type='barcode')
    lainuri.event_queue.push_event(event)
    assert lainuri.websocket_server.handle_one_event(5) == event
    assert event == lainuri.event_queue.history[3]

  with subtests.test("Then a LECheckOutComplete-event is dispatched"):
    event = lainuri.websocket_server.handle_one_event(5)
    assert event == lainuri.event_queue.history[4]
    assert type(event) == le.LECheckOutComplete
    assert event.status == Status.SUCCESS

  with subtests.test("When the tag is checked out AGAIN!"):
    event = le.LECheckOut(item_barcode=tag.iso25680_get_primary_item_identifier(), user_barcode=good_user_barcode, tag_type='barcode')
    lainuri.event_queue.push_event(event)
    assert lainuri.websocket_server.handle_one_event(5) == event
    assert event == lainuri.event_queue.history[5]

  with subtests.test("Then a LECheckOutComplete-event is dispatched AGAIN"):
    event = lainuri.websocket_server.handle_one_event(5)
    assert event == lainuri.event_queue.history[6]
    assert type(event) == le.LECheckOutComplete

  with subtests.test("And the event succeeded due to item already checked out, but doesn't renew"):
    assert event.states == {"Checkout::Renew": True}
    assert event.status == Status.SUCCESS



def test_checkout_exception_item_not_found(subtests):
  global good_item_barcode, good_user_barcode
  tag = None
  borrower = None
  event = None
  assert lainuri.event_queue.flush_all()

  with subtests.test("Given an API authentication"):
    assert lainuri.koha_api.koha_api.authenticate()

  with subtests.test("When the tag is checked out"):
    event = le.LECheckOut(item_barcode='barcode-not-registered', user_barcode=good_user_barcode, tag_type='barcode')
    lainuri.event_queue.push_event(event)
    assert lainuri.websocket_server.handle_one_event(5) == event
    assert event == lainuri.event_queue.history[0]

  with subtests.test("Then a response event is generated"):
    event = lainuri.websocket_server.handle_one_event(5)
    assert event == lainuri.event_queue.history[1]
    assert type(event) == le.LECheckOutComplete

  with subtests.test("And the exception class matches"):
    assert event.status == Status.ERROR
    assert len(event.states) == 1
    assert event.states['exception']['type'] == 'NoItem'

