#!/usr/bin/python3

import context

import lainuri.db
import lainuri.db.receipt_template


def test_db_init():
  lainuri.db.init()
  assert lainuri.db.receipt_template.list_all()

def test_db_create():
  lainuri.db.create_database()
  assert lainuri.db.receipt_template.list_all()

def test_db_drop():
  lainuri.db.drop_database()
  assert not lainuri.db._db_exists()

def test_db_create_db_if_not_exists():
  lainuri.db.init()
  assert lainuri.db.receipt_template.list_all()

def test_db_not_recreate_db_if_exists():
  lainuri.db.init()
  assert lainuri.db.receipt_template.list_all()
