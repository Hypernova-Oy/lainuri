#!/usr/bin/python3

import context

import lainuri.db


def test_db_init():
  lainuri.db.init()

def test_db_create():
  lainuri.db.create_database()
  assert lainuri.db.receipt_templates_list()

def test_db_drop():
  lainuri.db.drop_database()
  #lainuri.db.init() # wait for implicit init() when connection doesnt exist
  assert not lainuri.db._db_exists()
  assert not lainuri.db.conn

def test_db_create_db_if_not_exists():
  lainuri.db.create_db_if_not_exists()
  assert lainuri.db.receipt_templates_list()

def test_db_not_recreate_db_if_exists():
  lainuri.db.create_db_if_not_exists()
  assert lainuri.db.receipt_templates_list()
