#!/usr/bin/python3

import context
import lainuri.config

from lainuri.exception import NoResults
import lainuri.exception.ils as exception_ils
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
  context.assert_raises('Testing bad authentication', exception_ils.InvalidUser, 'l-t-dev-bad',
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
  context.assert_raises('Testing bad enduser', exception_ils.NoUser, 'l-t-u-bad',
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
  context.assert_raises('Testing bad item barcode', exception_ils.NoItem, 'l-t-i-bad',
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
  context.assert_raises('Testing bad biblionumber', NoResults, '9999999999', lambda: MARCRecord(koha_api.get_record(9999999999)))

  koha_api.current_event_id = 'marc-9'
  record = MARCRecord(koha_api.get_record(item['biblionumber']))
  assert record.author() or record.title() or record.book_cover_url()

  item_bib = get_fleshed_item_record(item['barcode'])
  assert item_bib['item_barcode'] == 'l-t-i-good'
  assert item_bib['edition']
  assert item_bib['title']
  assert item_bib['author']
  assert item_bib['book_cover_url']
