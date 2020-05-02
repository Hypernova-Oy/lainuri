#!/usr/bin/python3

import context
from lainuri.config import get_config

import time
import unittest.mock

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
  assert lainuri.event_queue.flush_all()

  with subtests.test("Given a rfid reader which has RFID tags in reading radius"):
    rfid_reader = rfid.get_rfid_reader()
    assert len(rfid_reader.do_inventory(no_events=True).tags_present) > 0

  with subtests.test("And a RFID tag"):
    tags_present = rfid.get_current_inventory_status()
    assert len(tags_present) > 0
    tag = tags_present[0]

  with subtests.test("And the RFID tag is registered in the test Koha instance as a circulable Item"):
    assert tag.iso25680_get_primary_item_identifier() == good_item_barcode

  with subtests.test("When the tag security status is set"):
    event = le.LESetTagAlarm(item_barcode=tag.iso25680_get_primary_item_identifier(), on=True, recipient='server')
    lainuri.event_queue.push_event(event)
    assert lainuri.websocket_server.handle_one_event(5) == event

  with subtests.test("Then a response event is generated"):
    event = lainuri.websocket_server.handle_one_event(5)
    assert event == lainuri.event_queue.history[1]
    assert type(event) == le.LESetTagAlarmComplete
    assert event.status == Status.SUCCESS
    assert event.on == True

  with subtests.test("And the gate security alarm is enabled"):
    assert tag.afi() == get_config('devices.rfid-reader.afi-checkin')

  with subtests.test("When the tag security status is unset"):
    event = le.LESetTagAlarm(item_barcode=tag.iso25680_get_primary_item_identifier(), on=False, recipient='server')
    lainuri.event_queue.push_event(event)
    assert lainuri.websocket_server.handle_one_event(5) == event

  with subtests.test("And the gate security alarm is disabled"):
    assert tag.afi() == get_config('devices.rfid-reader.afi-checkout')

  with subtests.test("Then a response-event is dispatched"):
    event = lainuri.websocket_server.handle_one_event(5)
    assert event == lainuri.event_queue.history[3]
    assert type(event) == le.LESetTagAlarmComplete
    assert event.status == Status.SUCCESS
    assert event.on == False

def test_gate_security_double_check_performance(subtests):
  rfid_reader = rfid.get_rfid_reader()

  tags_present = rfid.get_current_inventory_status()
  assert len(tags_present) > 0
  tag = tags_present[0]

  lainuri.config.write_config('devices.rfid-reader.double-check-gate-security', True)
  start_time_1 = time.time()
  for i in range(0,5):
    rfid._set_tag_gate_alarm_afi(rfid_reader, tag, flag_on=True)
    rfid._set_tag_gate_alarm_afi(rfid_reader, tag, flag_on=False)
  duration_1 = time.time() - start_time_1

  lainuri.config.write_config('devices.rfid-reader.double-check-gate-security', False)
  start_time_2 = time.time()
  for i in range(0,5):
    rfid._set_tag_gate_alarm_afi(rfid_reader, tag, flag_on=True)
    rfid._set_tag_gate_alarm_afi(rfid_reader, tag, flag_on=False)
  duration_2 = time.time() - start_time_2

  print(f"Extra check: '{duration_1}'. No check: '{duration_2}'.")
  assert duration_1 > (duration_2 * 1.33)

def test_set_gate_security_status_for_missing_tag(subtests):
  event = None

  assert lainuri.event_queue.flush_all()

  with subtests.test("Given a rfid reader which has RFID tags in reading radius"):
    rfid_reader = rfid.get_rfid_reader()

  with subtests.test("When the tag security status is set for an imaginary tag"):
    event = le.LESetTagAlarm(item_barcode='imaginary-primary-item-identifier', on=True, recipient='server')
    lainuri.event_queue.push_event(event)
    assert lainuri.websocket_server.handle_one_event(5) == event
    assert event == lainuri.event_queue.history[0]

  with subtests.test("Then a response event in generated"):
    event = lainuri.websocket_server.handle_one_event(5)
    assert event == lainuri.event_queue.history[1]
    assert type(event) == le.LESetTagAlarmComplete

  with subtests.test("And the event status is TagNotDetected"):
    assert event.status == Status.ERROR
    assert event.states['exception']['type'] == exception_rfid.TagNotDetected.__name__


def test_set_gate_security_status_for_failing_command(subtests):
  event = None

  assert lainuri.event_queue.flush_all()

  with unittest.mock.patch('lainuri.rfid_reader._handle_retriable_exception', side_effect=lainuri.rfid_reader._handle_retriable_exception) as mock_handle_retriable_exception:

    with unittest.mock.patch(
      'lainuri.rfid_reader._set_tag_gate_alarm_afi',
      side_effect=lainuri.rfid_reader.exception_rfid.RFIDCommand('test-command','mocked test rfid command execution to fail')) as mock_set_tag_gate_alarm_eas:


      with subtests.test("Given a rfid reader which has RFID tags in reading radius"):
        rfid_reader = rfid.get_rfid_reader()

      with subtests.test("And a RFID tag"):
        tags_present = rfid.get_current_inventory_status()
        assert len(tags_present) > 0
        tag = tags_present[0]

      with subtests.test("And the RFID tag is registered in the test Koha instance as a circulable Item"):
        assert tag.iso25680_get_primary_item_identifier() == good_item_barcode

      with subtests.test("When the tag security status is set for an imaginary tag"):
        event = le.LESetTagAlarm(item_barcode=good_item_barcode, on=True, recipient='server')
        lainuri.event_queue.push_event(event)
        assert lainuri.websocket_server.handle_one_event(5) == event
        assert event == lainuri.event_queue.history[0]

      with subtests.test("Then a response event in generated"):
        event = lainuri.websocket_server.handle_one_event(5)
        assert event == lainuri.event_queue.history[1]
        assert type(event) == le.LESetTagAlarmComplete

      with subtests.test("And the event status is ERROR with expected exception"):
        assert event.states['exception']['type'] == exception_rfid.RFIDCommand.__name__
        assert event.status == Status.ERROR

      with subtests.test("And the operation was retried until failure"):
        assert mock_handle_retriable_exception.call_count == 3
