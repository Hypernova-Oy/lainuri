from lainuri.config import get_config
from lainuri.logging_context import logging
log = logging.getLogger(__name__)

import os
import pathlib
import pugsql
import re
import sqlite3
import yoyo

conn, c = (None, None)

def _get_db_connstr() -> str:
  return f"sqlite:///{_get_db_path()}"

def _get_db_path():
  return 'lainuri.sqlite3.db'

def init() -> list:
  _init_sqlite3()
  if not _db_exists(): create_database()

def _init_sqlite3():
  global conn, c
  conn = sqlite3.connect(_get_db_path())
  c = conn.cursor()
  c.arraysize = 1000
  c.execute("PRAGMA foreign_keys = true;")
  c.execute("PRAGMA encoding = 'UTF-8';")

def dbh():
  global conn, c
  if not conn: init()
  return (conn, c)

def _db_exists():
  global conn, c
  if (not (conn and c)) and (not pathlib.Path(_get_db_path()).exists()): return False
  try:
    c.execute("SELECT * FROM receipt_templates")
  except sqlite3.Error as e:
    if str(e) == "no such table: receipt_templates": return False
    else: raise e
  return True

def create_database():
  log.info(f"Creating database '{_get_db_connstr()}'")
  upgrade_database_schema()

def upgrade_database_schema():
  migration_files_dir = str(pathlib.Path(__file__).parent / 'schema')
  backend = yoyo.get_backend(_get_db_connstr())
  migrations = yoyo.read_migrations(migration_files_dir)
  if not migrations: raise Exception(f"No DB install files present in '{migration_files_dir}'")
  #with backend.lock(): # This is bugged in yoyo-imports presently, as the lock is not release when contextmanager returns
  backend.apply_migrations(backend.to_apply(migrations))


"""
sqlite3 has no way of telling if the connection was closed or not, aside of catching exceptions
"""
def close_db():
  global conn, c
  conn.close()
  conn = None
  c = None

"""
To recereate the DB, call init() again.
"""
def drop_database():
  log.warning(f"Dropping database '{_get_db_path()}'")
  (conn, c) = dbh()
  if conn:
    close_db()
  pathlib.Path(_get_db_path()).unlink()
