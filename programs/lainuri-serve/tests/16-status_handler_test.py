#!/usr/bin/python3

import context
from lainuri.config import get_config

import time
import pytest_subtests
import unittest.mock

import lainuri.websocket_server
from lainuri.constants import Status
import lainuri.event as le
import lainuri.koha_api
import lainuri.rfid_reader as rfid


good_item_barcode = '1620154429'

def test_rfid_reader_get_tag_inventory_via_event_queue(subtests):
  global good_item_barcode
  tag = None
  borrower = None
  event = None

  assert get_config('devices.rfid-reader.enabled') == True
  assert lainuri.event_queue.flush_all()

  with subtests.test("Given an API authentication"):
    assert lainuri.koha_api.koha_api.authenticate()

  with subtests.test("And a rfid reader which has RFID tags in reading radius"):
    rfid_reader = rfid.get_rfid_reader()
    assert len(rfid_reader.do_inventory(no_events=True).tags_present) > 0

  with subtests.test("When inventory of RFID tags present is requested"):
    event = le.LERFIDTagsPresentRequest()
    lainuri.event_queue.push_event(event)
    assert lainuri.websocket_server.handle_one_event(5) == event
    assert event == lainuri.event_queue.history[0]

  with subtests.test("Then a response event is generated"):
    event = lainuri.websocket_server.handle_one_event(5)
    assert event == lainuri.event_queue.history[1]
    assert type(event) == le.LERFIDTagsPresent
    assert getattr(event.message['tags_present'][0], 'states', None) == None
    assert event.message['tags_present'][0]['status'] == Status.SUCCESS
    assert event.tags_present[0].iso25680_get_primary_item_identifier() == good_item_barcode

def test_get_public_config(subtests):
  assert lainuri.event_queue.flush_all()

  with subtests.test("When public configuration is requested"):
    event = le.LEConfigGetpublic()
    lainuri.event_queue.push_event(event)
    assert lainuri.websocket_server.handle_one_event(5) == event
    assert event == lainuri.event_queue.history[0]

  with subtests.test("Then a response event is generated"):
    event = lainuri.websocket_server.handle_one_event(5)
    assert event == lainuri.event_queue.history[1]
    assert type(event) == le.LEConfigGetpublic_Response
    assert event.config['i18n']['default_locale']
    assert event.config['ui']['use_bookcovers']
