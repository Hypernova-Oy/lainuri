#!/usr/bin/python3

import context
from lainuri.config import get_config

import pytest_subtests

import context.mock_koha_api_checkin_responses

import lainuri.websocket_server
import lainuri.koha_api
from lainuri.constants import Status
import lainuri.event as le


good_item_barcode = '1620154429'
good_user_barcode = '23529000035676'

def mock_handle_html(html_data_source):
  api = lainuri.koha_api.koha_api
  (barcode, soup) = html_data_source()
  return api._checkin_check_statuses(barcode, soup, *api._parse_html(soup))

def test_statuses_mock_checkin__transfer_with_outstanding_fines_01():
  (status, states) = mock_handle_html(context.mock_koha_api_checkin_responses.transfer_with_outstanding_fines_01)

  assert status == Status.SUCCESS
  assert states['outstanding_fines'] == '4.00'
  assert states['return_to_another_branch'] == 'Kouvolan kampuskirjasto'
  assert len(states) == 2

def test_statuses_mock_checkin__hold_transfer_with_outstanding_fines_01():
  (status, states) = mock_handle_html(context.mock_koha_api_checkin_responses.hold_transfer_with_outstanding_fines_01)

  assert status == Status.SUCCESS
  assert states['outstanding_fines'] == '4.00'
  assert states['hold_found'] == '224247'
  assert states['return_to_another_branch'] == 'Savonlinnan kampuskirjasto'
  assert len(states) == 3

def test_statuses_mock_checkin__hold_with_outstanding_fines_01():
  (status, states) = mock_handle_html(context.mock_koha_api_checkin_responses.hold_with_outstanding_fines_01)

  assert status == Status.SUCCESS
  assert states['outstanding_fines'] == '4.00'
  assert states['hold_found'] == '142261'
  assert len(states) == 2

def test_statuses_mock_checkin__simple_checkin_01():
  (status, states) = mock_handle_html(context.mock_koha_api_checkin_responses.simple_checkin_01)

  assert status == Status.SUCCESS
  assert len(states) == 0



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
