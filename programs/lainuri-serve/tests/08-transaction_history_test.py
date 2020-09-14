#!/usr/bin/python3

import context
import context.transaction_histories

import datetime
import sqlite3
import time

import lainuri.db
import lainuri.db.transaction_history


def test_db_init():
  lainuri.db.init()

def test_clear():
  rv = lainuri.db.transaction_history.clear()
  assert rv == 0 or rv

def test_post1():
  rv = lainuri.db.transaction_history.post(context.transaction_histories.item1)
  assert rv

def test_list1_checkins():
  rv = lainuri.db.transaction_history.list_between(
    transaction_date_start='1975-01-01 01:15:22',
    transaction_date_end=datetime.datetime.fromtimestamp(time.time()+3600).isoformat('T'),
    transaction_types=['checkin'])
  context.transaction_histories.assert_item1(rv, 0)
  assert len(rv) == 1

def test_list1_checkouts():
  rv = lainuri.db.transaction_history.list_between(transaction_date_start=time.time()-10, transaction_date_end=time.time()+10, transaction_types=['checkout'])
  assert len(rv) == 0

def test_post2():
  rv = lainuri.db.transaction_history.post(context.transaction_histories.item2)
  assert rv

def test_list2():
  rv = lainuri.db.transaction_history.list_between(transaction_date_start=time.time()-10, transaction_date_end=time.time()+10, transaction_types=['checkin','checkout'])
  context.transaction_histories.assert_item1(rv, 0)
  context.transaction_histories.assert_item2(rv, 1)
  assert len(rv) == 2

def test_post3_bad_transaction_type():
  context.assert_raises('FOREIGN KEY exception is expected', sqlite3.IntegrityError, 'FOREIGN KEY constraint failed',
    lambda: lainuri.db.transaction_history.post({
      'transaction_type':'checkouch', 'borrower_barcode':'13', 'item_barcode':'3', 'transaction_date':time.time()
    })
  )

def test_list3():
  rv = lainuri.db.transaction_history.list_between(transaction_date_start=time.time()-3600, transaction_date_end=time.time()+3600, transaction_types=['checkin','checkout'])
  context.transaction_histories.assert_item1(rv, 0)
  context.transaction_histories.assert_item2(rv, 1)
  assert len(rv) == 2

def test_get_for_borrower():
  rv = lainuri.db.transaction_history.post(context.transaction_histories.item3)
  assert rv

  rv = lainuri.db.transaction_history.get_for_borrower(12)
  context.transaction_histories.assert_item2(rv, 0)
  context.transaction_histories.assert_item3(rv, 1)
  assert len(rv) == 2
  rv = lainuri.db.transaction_history.get_for_borrower(12, transaction_types=['checkin'])
  assert len(rv) == 0

def test_list4_isodates():
  rv = lainuri.db.transaction_history.list_between(transaction_date_start='1975-01-01 01:15:22', transaction_date_end='1985-01-01 01:15:22')
  assert len(rv) == 0
