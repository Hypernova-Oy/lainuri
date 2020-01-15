#!/usr/bin/python3

import context
import lainuri.config

from lainuri.exceptions import InvalidUser, NoResults
from lainuri.koha_api import KohaAPI, MARCRecord

api = KohaAPI()
borrower = {}
item = {}
record = {}

def test_authenticate():
  global borrower, item, record
  api.current_event_id = 'event-id-1'
  assert api.authenticated() == 0

  # Lainuri boots and whenever authentication times out.
  lainuri.config.c['koha']['userid'] = 'l-t-dev-bad'
  lainuri.config.c['koha']['password'] = 'bad_pass'
  api.current_event_id = 'event-id-2'
  assert_raises('Testing bad authentication', InvalidUser, 'l-t-dev-bad',
    lambda: api.authenticate()
  )

  lainuri.config.c['koha']['userid'] = 'l-t-dev-good'
  lainuri.config.c['koha']['password'] = 'correct_credentials_password-!'
  api.current_event_id = 'event-id-3'
  assert api.authenticate()
  assert api.sessionid

def test_user_login():
  global borrower, item, record
  api.current_event_id = 'auth-user-4'
  assert_raises('Testing bad enduser', NoResults, 'l-t-u-bad',
    lambda: api.authenticate_user('l-t-u-bad')
  )

  # Borrower login event
  api.current_event_id = 'auth-user-5'
  borrower = api.authenticate_user('l-t-u-good')
  assert borrower['borrowernumber']
  assert borrower['cardnumber'] == borrower['cardnumber']

def test_get_item():
  global borrower, item, record
  api.current_event_id = 'item-6'
  assert_raises('Testing bad item barcode', NoResults, 'l-t-i-bad',
    lambda: api.get_item('l-t-i-bad')
  )

  # New RFID tag or barcode read after user login
  api.current_event_id = 'item-7'
  item = api.get_item('l-t-i-good')
  assert item['itemnumber']
  assert item['biblionumber']

def test_enrich_rfid_tag_with_marc():
  global borrower, item, record
  api.current_event_id = 'marc-8'
  assert_raises('Testing bad biblionumber', NoResults, '9999999999', lambda: MARCRecord(api.get_record(9999999999)))

  api.current_event_id = 'marc-9'
  record = MARCRecord(api.get_record(item['biblionumber']))
  assert record.author() or record.title() or record.book_cover_url()

def test_checkin():
  global borrower, item, record
  api.current_event_id = 'checkin-10'
  statuses = api.checkin(item['barcode'])
  assert statuses['status'] == 'success'

def test_checkout():
  global borrower, item, record
  api.current_event_id = 'checkout-11'
  statuses = api.checkout(item['barcode'], borrower['borrowernumber'])
  assert statuses['status'] == 'success'

def test_receipt():
  global borrower, item, record
  api.current_event_id = 'receipt-12'
  assert api.receipt(borrower['borrowernumber'])


def assert_raises(name, e_class, e_string, cb):
  try:
    cb()
    raise AssertionError(name + " failed to raise! " + cb)
  except Exception as e:
    assert type(e) == e_class
    assert e_string in str(e)
