#!/usr/bin/python3

import context
from lainuri.config import get_config

import json
import time
import pytest_subtests

import context.mock_koha_api_checkout_responses

import lainuri.db.transaction_history
import lainuri.websocket_server
import lainuri.koha_api
from lainuri.constants import Status
import lainuri.event as le
import lainuri.websocket_handlers.checkin
import lainuri.websocket_handlers.checkout
import lainuri.rfid_reader as rfid


good_item_barcode = '1620154429'
good_user_barcode = '23529000035676'

def mock_handle_html(html_data_source):
  api = lainuri.koha_api.koha_api
  (barcode, soup) = html_data_source()
  return api._checkout_check_statuses(barcode, soup, *api._parse_html(soup))

def test_statuses_mock_checkout__needs_confirmation_01():
  (status, states) = mock_handle_html(context.mock_koha_api_checkout_responses.needs_confirmation_01)

  assert status == Status.ERROR
  assert states['needs_confirmation'] == True
  assert len(states) == 1

def test_statuses_mock_checkout__issueconfirmed_01():
  (status, states) = mock_handle_html(context.mock_koha_api_checkout_responses.issueconfirmed_01)

  assert status == Status.SUCCESS
  assert len(states) == 0

def test_statuses_mock_availability__hold_waiting_01():
  availability = json.loads('[{"availability":{"available":true,"confirmations":{"Item::Held":{"borrowernumber":1266,"hold_queue_length":1,"status":"Waiting"}}},"barcode":"1620027464","biblioitemnumber":119736,"biblionumber":119736,"ccode":null,"ccode_description":null,"enumchron":null,"hold_queue_length":1,"holding_id":null,"holdingbranch":"MIK","homebranch":"MIK","itemcallnumber":"159.9 REISER","itemcallnumber_display":"159.9 REISER","itemnotes":null,"itemnumber":21843,"location":"LAINA","location_description":"Lainattavat","sub_description":null,"sub_location":null}]')[0]['availability']
  status = lainuri.websocket_handlers.checkout._check_availability_statuses(availability)
  assert status == Status.ERROR
  assert availability['confirmations']['Item::Held::Waiting'] == True

def test_statuses_mock_availability__hold_pending_01():
  availability = json.loads('[{"availability":{"available":true,"confirmations":{"Item::Held":{"borrowernumber":1266,"hold_queue_length":1,"status":"Reserved"}}},"barcode":"1620154466","biblioitemnumber":141810,"biblionumber":141810,"ccode":null,"ccode_description":null,"enumchron":null,"hold_queue_length":1,"holding_id":null,"holdingbranch":"MIK","homebranch":"MIK","itemcallnumber":"17 OKSANEN","itemcallnumber_display":"17 OKSANEN","itemnotes":null,"itemnumber":102120,"location":"LAINA","location_description":"Lainattavat","sub_description":null,"sub_location":null}]')[0]['availability']
  status = lainuri.websocket_handlers.checkout._check_availability_statuses(availability)
  assert status == None

def test_statuses_mock_availability__renew_01():
  availability = json.loads('[{"availability":{"available":true,"confirmations":{"Checkout::Renew":{}}},"barcode":"1620146356","biblioitemnumber":142316,"biblionumber":142316,"ccode":null,"ccode_description":null,"enumchron":null,"hold_queue_length":0,"holding_id":null,"holdingbranch":"MIK","homebranch":"MIK","itemcallnumber":"59.1 ANATOMIA","itemcallnumber_display":"59.1 ANATOMIA","itemnotes":null,"itemnumber":71813,"location":"LAINA","location_description":"Lainattavat","sub_description":null,"sub_location":null}]')[0]['availability']
  status = lainuri.websocket_handlers.checkout._check_availability_statuses(availability)
  assert status == Status.SUCCESS



def test_checkout_barcode_via_event_queue(subtests):
  global good_item_barcode, good_user_barcode
  borrower = None
  assert lainuri.event_queue.flush_all()
  lainuri.db.transaction_history.clear()

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
    assert event.states == {}
    assert event.item_barcode == good_item_barcode
    assert event.status == Status.SUCCESS

  with subtests.test("And a transaction_history-event is persisted"):
    rv = lainuri.db.transaction_history.list_between(transaction_types=['checkout'])
    assert rv[0]['borrower_barcode'] == good_user_barcode
    assert rv[0]['item_barcode'] == good_item_barcode


def test_checkout_rfid_via_event_queue(subtests):
  global good_item_barcode
  tag = None
  borrower = None
  event = None
  assert lainuri.event_queue.flush_all()
  lainuri.db.transaction_history.clear()

  assert get_config('devices.rfid-reader.enabled') == True

  with subtests.test("Given an API authentication"):
    assert lainuri.koha_api.koha_api.authenticate()

  with subtests.test("And a rfid reader which has RFID tags in reading radius"):
    rfid_reader = rfid.get_rfid_reader()
    assert len(rfid_reader.do_inventory(no_events=True).tags_present) > 0

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
    assert event == lainuri.event_queue.history[0]

  with subtests.test("Then a response event is generated"):
    event = lainuri.websocket_server.handle_one_event(5)
    assert event == lainuri.event_queue.history[1]
    assert type(event) == le.LECheckInComplete
    assert event.status == Status.SUCCESS

  with subtests.test("And a transaction_history-event is persisted"):
    rv = lainuri.db.transaction_history.list_between(transaction_types=['checkin'])
    assert rv[0]['borrower_barcode'] == None
    assert rv[0]['item_barcode'] == good_item_barcode

  with subtests.test("When the tag is checked out"):
    event = le.LECheckOut(item_barcode=tag.iso25680_get_primary_item_identifier(), user_barcode=good_user_barcode, tag_type='barcode')
    lainuri.event_queue.push_event(event)
    assert lainuri.websocket_server.handle_one_event(5) == event
    assert event == lainuri.event_queue.history[2]

  with subtests.test("Then a LECheckOutComplete-event is dispatched"):
    event = lainuri.websocket_server.handle_one_event(5)
    assert event == lainuri.event_queue.history[3]
    assert event.states == {}
    assert type(event) == le.LECheckOutComplete
    assert event.status == Status.SUCCESS

  with subtests.test("And a transaction_history-event is persisted"):
    rv = lainuri.db.transaction_history.list_between(transaction_types=['checkout'])
    assert rv[0]['borrower_barcode'] == good_user_barcode
    assert rv[0]['item_barcode'] == good_item_barcode

  with subtests.test("When the tag is checked out AGAIN!"):
    event = le.LECheckOut(item_barcode=tag.iso25680_get_primary_item_identifier(), user_barcode=good_user_barcode, tag_type='barcode')
    lainuri.event_queue.push_event(event)
    assert lainuri.websocket_server.handle_one_event(5) == event
    assert event == lainuri.event_queue.history[4]

  with subtests.test("Then a LECheckOutComplete-event is dispatched AGAIN"):
    event = lainuri.websocket_server.handle_one_event(5)
    assert event == lainuri.event_queue.history[5]
    assert type(event) == le.LECheckOutComplete

  with subtests.test("And the event succeeded due to item already checked out, but doesn't renew"):
    assert event.states == {"Checkout::Renew": True}
    assert event.status == Status.SUCCESS

  with subtests.test("And a transaction_history-event is persisted"):
    rv = lainuri.db.transaction_history.list_between(transaction_types=['checkout'])
    assert rv[1]['borrower_barcode'] == good_user_barcode
    assert rv[1]['item_barcode'] == good_item_barcode


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

