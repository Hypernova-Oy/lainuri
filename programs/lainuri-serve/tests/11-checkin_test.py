#!/usr/bin/python3

import context
from lainuri.config import get_config

import pytest_subtests

import lainuri.websocket_server
import lainuri.koha_api
from lainuri.constants import Status
import lainuri.event as le


good_item_barcode = '1620154429'
good_user_barcode = '23529000035676'

def test_checkin_barcode_via_event_queue(subtests):
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
    assert event.states['return_to_another_branch'] == 'Centerville'
    assert event.status == Status.SUCCESS


def test_checkin_exception_item_not_found(subtests):
  global good_item_barcode
  tag = None
  borrower = None
  event = None
  assert lainuri.event_queue.flush_all()

  with subtests.test("Given an API authentication"):
    assert lainuri.koha_api.koha_api.authenticate()

  with subtests.test("When the tag is checked in"):
    event = le.LECheckIn(item_barcode='barcode-not-registered', tag_type='barcode')
    lainuri.event_queue.push_event(event)
    assert lainuri.websocket_server.handle_one_event(5) == event
    assert event == lainuri.event_queue.history[0]

  with subtests.test("Then a response event is generated"):
    event = lainuri.websocket_server.handle_one_event(5)
    assert event == lainuri.event_queue.history[1]
    assert type(event) == le.LECheckInComplete

  with subtests.test("And the exception class matches"):
    assert event.status == Status.ERROR
    assert len(event.states) == 1
    assert event.states['exception']['type'] == 'NoItem'

