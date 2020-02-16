#!/usr/bin/python3

import context
import lainuri.config

from lainuri.exceptions import InvalidUser, NoResults
from lainuri.koha_api import koha_api, MARCRecord, get_fleshed_item_record

borrower = {}
item = {}
record = {}

def test_authenticate():
  global borrower, item, record
  koha_api.current_event_id = 'event-id-1'
  assert koha_api.authenticated() == 0

  # Lainuri boots and whenever authentication times out.
  lainuri.config.c['koha']['userid'] = 'l-t-dev-bad'
  lainuri.config.c['koha']['password'] = 'bad_pass'
  koha_api.current_event_id = 'event-id-2'
  assert_raises('Testing bad authentication', InvalidUser, 'l-t-dev-bad',
    lambda: koha_api.authenticate()
  )

  lainuri.config.c['koha']['userid'] = 'l-t-dev-good'
  lainuri.config.c['koha']['password'] = 'correct_credentials_password-!'
  koha_api.current_event_id = 'event-id-3'
  assert koha_api.authenticate()
  assert koha_api.sessionid

def test_user_login():
  global borrower, item, record
  koha_api.current_event_id = 'auth-user-4'
  assert_raises('Testing bad enduser', NoResults, 'l-t-u-bad',
    lambda: koha_api.authenticate_user('l-t-u-bad')
  )

  # Borrower login event
  koha_api.current_event_id = 'auth-user-5'
  borrower = koha_api.authenticate_user('l-t-u-good')
  assert borrower['borrowernumber']
  assert borrower['cardnumber'] == 'l-t-u-good'

def test_get_item():
  global borrower, item, record
  koha_api.current_event_id = 'item-6'
  assert_raises('Testing bad item barcode', NoResults, 'l-t-i-bad',
    lambda: koha_api.get_item('l-t-i-bad')
  )

  # New RFID tag or barcode read after user login
  koha_api.current_event_id = 'item-7'
  item = koha_api.get_item('l-t-i-good')
  assert item['itemnumber']
  assert item['biblionumber']

def test_enrich_rfid_tag_with_marc():
  global borrower, item, record
  koha_api.current_event_id = 'marc-8'
  assert_raises('Testing bad biblionumber', NoResults, '9999999999', lambda: MARCRecord(koha_api.get_record(9999999999)))

  koha_api.current_event_id = 'marc-9'
  record = MARCRecord(koha_api.get_record(item['biblionumber']))
  assert record.author() or record.title() or record.book_cover_url()

  item_bib = get_fleshed_item_record(item['barcode'], tag_type='rfid')
  assert item_bib['item_barcode'] == 'l-t-i-good'
  assert item_bib['edition']
  assert item_bib['title']
  assert item_bib['author']
  assert item_bib['book_cover_url']

def test_checkin():
  global borrower, item, record
  koha_api.current_event_id = 'checkin-10'
  (status, states) = koha_api.checkin(item['barcode'])
  assert status == 'success'

def test_checkout():
  global borrower, item, record
  koha_api.current_event_id = 'checkout-11'
  (status, states) = koha_api.checkout(item['barcode'], borrower['borrowernumber'])
  assert status == 'success'

def test_receipt():
  global borrower, item, record
  koha_api.current_event_id = 'receipt-12'
  assert koha_api.receipt(borrower['borrowernumber'])

def assert_raises(name, e_class, e_string, cb):
  try:
    cb()
    raise AssertionError(name + " failed to raise! " + cb)
  except Exception as e:
    assert type(e) == e_class
    assert e_string in str(e)
