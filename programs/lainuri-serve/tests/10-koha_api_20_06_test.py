#!/usr/bin/python3

import json
import unittest.mock

import context
import lainuri.config

import lainuri.event
import lainuri.event_queue
from lainuri.exception import NoResults
import lainuri.exception.ils as exception_ils
from lainuri.koha_api import koha_api, MARCRecord, get_fleshed_item_record

borrower = {}
item = {}
record = {}

def test_authenticate():
  global borrower, item, record
  koha_api.current_event_id = 'event-id-1'
  koha_api.deauthenticate()
  assert koha_api.authenticated() == 0

  good_user = lainuri.config.c['koha']['userid']
  good_pass = lainuri.config.c['koha']['password']

  # Lainuri boots and whenever authentication times out.
  lainuri.config.c['koha']['userid'] = 'l-t-dev-bad'
  lainuri.config.c['koha']['password'] = 'bad_pass'
  koha_api.current_event_id = 'event-id-2'
  context.assert_raises('Testing bad authentication', exception_ils.InvalidUser, 'l-t-dev-bad',
    lambda: koha_api.authenticate()
  )

  lainuri.config.c['koha']['userid'] = good_user
  lainuri.config.c['koha']['password'] = good_pass
  koha_api.current_event_id = 'event-id-3'
  assert koha_api.authenticate()
  assert koha_api.sessionid

def test_user_login():
  global borrower, item, record
  koha_api.current_event_id = 'auth-user-4'
  context.assert_raises('Testing bad enduser', exception_ils.NoUser, 'l-t-u-bad',
    lambda: koha_api.authenticate_user('l-t-u-bad')
  )

  # Borrower login event
  koha_api.current_event_id = 'auth-user-5'
  borrower = koha_api.authenticate_user(lainuri.config.c['koha']['userid'])
  assert borrower['patron_id']
  assert borrower['borrowernumber']
  assert borrower['cardnumber'] == lainuri.config.c['koha']['userid']

def test_permission_missing_dispatches_LEException():
  lainuri.event_queue.flush_all()

  context.assert_raises('Testing missing REST API permissions', exception_ils.PermissionMissing, 'order_manage',
    lambda: koha_api.get_order_1()
  )
  event = lainuri.event_queue.pop_event()
  assert type(event) == lainuri.event.LEException
  assert event.etype == 'PermissionMissing'
  assert len(event.description) > 10
  assert len(event.trace) > 10

def test_get_item():
  global borrower, item, record
  koha_api.current_event_id = 'item-6'
  context.assert_raises('Testing bad item barcode', exception_ils.NoItem, 'l-t-i-bad',
    lambda: koha_api.get_item('l-t-i-bad')
  )

  # New RFID tag or barcode read after user login
  koha_api.current_event_id = 'item-7'
  item = koha_api.get_item('kis12345')
  assert item['item_id']
  assert item['itemnumber']
  assert item['biblio_id']
  assert item['biblionumber']

def test_enrich_rfid_tag_with_marc():
  global borrower, item, record
  koha_api.current_event_id = 'marc-8'
  context.assert_raises('Testing bad biblionumber', NoResults, '9999999999', lambda: MARCRecord(koha_api.get_record(9999999999)))

  koha_api.current_event_id = 'marc-9'
  record = MARCRecord(koha_api.get_record(item['biblionumber']))
  assert record.author() or record.title() or record.book_cover_url()

  item_bib = get_fleshed_item_record(item['barcode'])
  assert item_bib['item_barcode'] == 'kis12345'
  #assert item_bib['edition']
  assert item_bib['title']
  assert item_bib['author']
  #assert item_bib['book_cover_url']

def test_availability():
  global borrower, item, record
  availability = koha_api.availability(borrowernumber=borrower['borrowernumber'], itemnumber=item['itemnumber'])
  assert availability['available'] == True

def test_availability_mocked_wait_for_pickup():
  mock_response = json.loads('[{"biblio_id":23,"cancellation_date":null,"cancellation_reason":null,"expiration_date":"2020-11-15","hold_date":"2020-10-29","hold_id":56,"item_id":"18","item_level":false,"item_type":null,"lowest_priority":false,"non_priority":false,"notes":"","patron_id":68,"pickup_library_id":"CPL","priority":0,"status":"W","suspended":false,"suspended_until":null,"timestamp":"2020-11-13T21:46:21+02:00","waiting_date":"2020-11-13"}]')
  with unittest.mock.patch.object(lainuri.koha_api.KohaAPI, '_receive_json', side_effect=lambda x: mock_response) as api_overload:
    availability = koha_api.availability(borrowernumber=borrower['borrowernumber'], itemnumber=item['itemnumber'])
    assert availability['available'] == False
    assert availability['confirmations']['Item::Held']['status'] == 'Waiting'

def test_checkout():
  global borrower, item, record
  (status, states) = koha_api.checkout(barcode=item['barcode'], borrowernumber=borrower['borrowernumber'])
  assert status
  assert states

def test_checkin():
  global borrower, item, record
  (status, states) = koha_api.checkin(item['barcode'])
  assert status
  assert states
