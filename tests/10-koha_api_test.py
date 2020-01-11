#!/usr/bin/python3

import context

from lainuri.koha_api import KohaAPI, MARCRecord

api = KohaAPI()

assert api.authenticated() == 0

# Lainuri boots and whenever authentication times out.
assert api.authenticate()

# Borrower login event
borrower = api.get_borrower('Aaltohel')
borrowernumber = borrower['borrowernumber']
assert borrowernumber

# New RFID tag or barcode read after user login
item = api.get_item('123')
itemnumber = item['itemnumber']
assert itemnumber
biblionumber = item['biblionumber']
assert biblionumber
record = MARCRecord(api.get_record(biblionumber))
assert record.author() or record.title() or record.book_cover_url()

# Checkin
api.checkin(item['barcode'])

# Checkout
api.checkout(item['barcode'], borrowernumber)

# Print receipt
assert api.receipt(borrowernumber)
