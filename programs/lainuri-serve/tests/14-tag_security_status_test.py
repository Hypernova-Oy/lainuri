#!/usr/bin/python3

import context
from lainuri.config import get_config

import time
import pytest_subtests

import lainuri.websocket_server
import lainuri.koha_api
from lainuri.constants import Status
import lainuri.event as le
import lainuri.exception.rfid as exception_rfid
import lainuri.websocket_handlers.checkin
import lainuri.websocket_handlers.checkout
import lainuri.rfid_reader as rfid


good_item_barcode = '1620154429'
good_user_barcode = '23529000035676'

def test_flip_flop_gate_security_status_via_event_queue(subtests):
  global good_item_barcode
  tag = None
  borrower = None
  event = None

  assert get_config('devices.rfid-reader.enabled') == True
  assert lainuri.event_queue.flush_history()

  with subtests.test("Given a rfid reader which has RFID tags in reading radius"):
    rfid_reader = rfid.RFID_Reader()
    assert len(rfid_reader.do_inventory().tags_new) > 0
    assert type(lainuri.websocket_server.handle_one_event(1)) == lainuri.event.LERFIDTagsNew

  with subtests.test("And a RFID tag"):
    tags_present = rfid.get_current_inventory_status()
    assert len(tags_present) > 0
    tag = tags_present[0]

  with subtests.test("And the RFID tag is registered in the test Koha instance as a circulable Item"):
    assert tag.iso25680_get_primary_item_identifier() == good_item_barcode

  with subtests.test("When the tag security status is set"):
    event = le.LESetTagAlarm(item_barcode=tag.iso25680_get_primary_item_identifier(), on=True, recipient='server')
    lainuri.event_queue.push_event(event)
    assert lainuri.websocket_server.handle_one_event(1) == event

  with subtests.test("Then a response event is generated"):
    event = lainuri.websocket_server.handle_one_event(1)
    assert event == lainuri.event_queue.history[2]
    assert type(event) == le.LESetTagAlarmComplete
    assert event.status == Status.SUCCESS
    assert event.on == True

  with subtests.test("And the gate security alarm is enabled"):
    assert tag.afi() == get_config('devices.rfid-reader.afi-checkin')

  with subtests.test("When the tag security status is unset"):
    event = le.LESetTagAlarm(item_barcode=tag.iso25680_get_primary_item_identifier(), on=False, recipient='server')
    lainuri.event_queue.push_event(event)
    assert lainuri.websocket_server.handle_one_event(1) == event

  with subtests.test("And the gate security alarm is disabled"):
    assert tag.afi() == get_config('devices.rfid-reader.afi-checkout')

  with subtests.test("Then a response-event is dispatched"):
    event = lainuri.websocket_server.handle_one_event(1)
    assert event == lainuri.event_queue.history[4]
    assert type(event) == le.LESetTagAlarmComplete
    assert event.status == Status.SUCCESS
    assert event.on == False

def test_set_gate_security_status_for_missing_tag(subtests):
  event = None

  assert lainuri.event_queue.flush_history()

  with subtests.test("Given a rfid reader which has RFID tags in reading radius"):
    rfid_reader = rfid.RFID_Reader()

  with subtests.test("When the tag security status is set for an imaginary tag"):
    event = le.LESetTagAlarm(item_barcode='imaginary-primary-item-identifier', on=True, recipient='server')
    lainuri.event_queue.push_event(event)
    assert lainuri.websocket_server.handle_one_event(1) == event
    assert event == lainuri.event_queue.history[0]

  with subtests.test("Then a response event in generated"):
    event = lainuri.websocket_server.handle_one_event(1)
    assert event == lainuri.event_queue.history[1]
    assert type(event) == le.LESetTagAlarmComplete

  with subtests.test("And the event status is TagNotDetected"):
    assert event.status == exception_rfid.TagNotDetected.__name__
