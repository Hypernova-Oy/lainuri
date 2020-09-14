
def assert_item1(rv, i):
  assert rv[i]['transaction_type'] == 'checkin'
  assert rv[i]['borrower_barcode'] == '11'
  assert rv[i]['item_barcode'] == '1'
def assert_item2(rv, i):
  assert rv[i]['transaction_type'] == 'checkout'
  assert rv[i]['borrower_barcode'] == '12'
  assert rv[i]['item_barcode'] == '2'
def assert_item3(rv, i):
  assert rv[i]['transaction_type'] == 'checkout'
  assert rv[i]['borrower_barcode'] == '12'
  assert rv[i]['item_barcode'] == '21'

item1 = {'transaction_type':'checkin', 'borrower_barcode':'11', 'item_barcode':'1'}
item2 = {'transaction_type':'checkout', 'borrower_barcode':'12', 'item_barcode':'2'}
item3 = {'transaction_type':'checkout', 'borrower_barcode':'12', 'item_barcode':'21'}
