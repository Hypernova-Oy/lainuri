#!/usr/bin/python3

import context
from lainuri.config import get_config

import json
import time
import pytest_subtests

import context.mock_koha_api_checkout_responses

import lainuri.websocket_server
import lainuri.koha_api
from lainuri.constants import Status
import lainuri.event as le
import lainuri.websocket_handlers.checkin
import lainuri.websocket_handlers.checkout
import lainuri.rfid_reader as rfid


good_item_barcode = '1620154429'

def test_fulldata_request(subtests):
  global good_item_barcode
  assert lainuri.event_queue.flush_all()

  with subtests.test("When a LEItemBibFullDataRequest event is handled"):
    event = lainuri.event_queue.push_event(le.LEItemBibFullDataRequest([good_item_barcode, 'bad-item-barcode']))
    assert lainuri.websocket_server.handle_one_event(5) == event
    assert event == lainuri.event_queue.history[0]
    assert type(event) == le.LEItemBibFullDataRequest

  with subtests.test("Then a LEItemBibFullDataResponse event is generated"):
    event = lainuri.websocket_server.handle_one_event(5)
    assert event == lainuri.event_queue.history[1]
    assert type(event) == le.LEItemBibFullDataResponse
    assert event.item_bibs[0].get('states', None) == None
    assert event.item_bibs[0]['status'] == Status.SUCCESS
    assert event.item_bibs[0]['item_barcode'] == good_item_barcode
    assert event.item_bibs[0]['title'] == '27 horas de estúdio. [Sound recording]'
    assert event.item_bibs[1]['states']['exception']['type'] == 'NoItem'
    assert event.item_bibs[1]['status'] == Status.ERROR
    assert event.item_bibs[1]['item_barcode'] == 'bad-item-barcode'
    assert event.item_bibs[1].get('title', None) == None

def test_rfid_inventory_triggered_fulldata_request(subtests):
  global good_item_barcode
  assert lainuri.event_queue.flush_all()

  assert get_config('devices.rfid-reader.enabled') == True

  with subtests.test("Given an API authentication"):
    assert lainuri.koha_api.koha_api.authenticate()

  with subtests.test("And a rfid reader which has RFID tags in reading radius"):
    rfid_reader = rfid.get_rfid_reader()
    assert len(rfid_reader.do_inventory(no_events=True).tags_present)
    rfid_reader.tags_present = [] #Flush detected tags, so we can trigger new-tags event

  with subtests.test("When the RFID reader polls for new tags"):
    assert len(rfid_reader.do_inventory(no_events=False).tags_present)

  with subtests.test("Then a LERFIDTagsNew event is generated"):
    event = lainuri.websocket_server.handle_one_event(5)
    assert event == lainuri.event_queue.history[0]
    assert type(event) == le.LERFIDTagsNew
    assert event.tags_new[0]['item_barcode'] == good_item_barcode
    assert event.tags_new[0]['tag_type'] == 'rfid'

  with subtests.test("And a LEItemBibFullDataRequest event is generated"):
    event = lainuri.websocket_server.handle_one_event(5)
    assert event == lainuri.event_queue.history[1]
    assert type(event) == le.LEItemBibFullDataRequest
    assert event.barcodes[0] == good_item_barcode

  with subtests.test("And a LEItemBibFullDataResponse event is generated"):
    event = lainuri.websocket_server.handle_one_event(5)
    assert event == lainuri.event_queue.history[2]
    assert type(event) == le.LEItemBibFullDataResponse
    assert event.item_bibs[0].get('states', None) == None
    assert event.item_bibs[0]['status'] == Status.SUCCESS
    assert event.item_bibs[0]['item_barcode'] == good_item_barcode
    assert event.item_bibs[0]['title'] == '27 horas de estúdio. [Sound recording]'

def test_barcode_read_triggered_fulldata_request(subtests):
  global good_item_barcode
  assert lainuri.event_queue.flush_all()

  with subtests.test("When a barcode is read"):
    lainuri.websocket_server.handle_barcode_read(None, good_item_barcode)

  with subtests.test("Then a LEBarcodeRead event is generated"):
    event = lainuri.websocket_server.handle_one_event(5)
    assert event == lainuri.event_queue.history[0]
    assert type(event) == le.LEBarcodeRead
    assert event.barcode == good_item_barcode

  with subtests.test("And a LEItemBibFullDataRequest event is generated"):
    event = lainuri.websocket_server.handle_one_event(5)
    assert event == lainuri.event_queue.history[1]
    assert type(event) == le.LEItemBibFullDataRequest
    assert event.barcodes[0] == good_item_barcode

  with subtests.test("And a LEItemBibFullDataResponse event is generated"):
    event = lainuri.websocket_server.handle_one_event(5)
    assert event == lainuri.event_queue.history[2]
    assert type(event) == le.LEItemBibFullDataResponse
    assert event.item_bibs[0].get('states', None) == None
    assert event.item_bibs[0]['status'] == Status.SUCCESS
    assert event.item_bibs[0]['item_barcode'] == good_item_barcode
    assert event.item_bibs[0]['title'] == '27 horas de estúdio. [Sound recording]'
