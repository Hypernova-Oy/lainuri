import lainuri.db.transaction_history
import pathlib
import re

in_file = pathlib.Path('bin/out').open('r')

# ST: ERROR EV: check-out-complete IBC: 167A0174667 UBC: 2600104874 TS: 13:10:58
parser = re.compile("^ST: (?P<status>.+?) EV: (?P<event>.+?) IBC: (?P<item>.+?) (:?UBC: (?P<borrower>.+?) )?TS: (?P<timestamp>.+?)$")
for row in in_file:
  match = parser.match(row)
  if not match: raise Exception(f"Couldn't match against '{row}'")

  lainuri.db.transaction_history.post({
    'transaction_type': (match.group('event') == "check-out-complete" and "checkout") or (match.group('event') == "check-in-complete" and "checkin"),
    'transaction_date': match.group('timestamp'),
    'borrower_barcode': match.group('borrower'),
    'item_barcode': match.group('item'),
  })
