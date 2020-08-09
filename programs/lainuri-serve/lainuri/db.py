from lainuri.config import get_config
from lainuri.logging_context import logging
log = logging.getLogger(__name__)

import os
import pathlib
import sqlite3

conn, c = (None, None)

def _get_db_connstr(test_mode: bool = False) -> str:
  if test_mode: return ':memory:'
  return 'lainuri.sqlite3.db'

def init(test_mode: bool = False) -> list:
  global conn, c
  conn = sqlite3.connect(_get_db_connstr())
  c = conn.cursor()
  c.arraysize = 1000
  create_db_if_not_exists()

def dbh():
  global conn, c
  if not conn: init()
  return (conn, c)

def create_db_if_not_exists():
  if not _db_exists(): create_database()

def _db_exists():
  global conn, c
  if (not (conn and c)) and (not pathlib.Path(_get_db_connstr()).exists()): return False
  try:
    c.execute("SELECT * FROM receipt_templates")
  except sqlite3.Error as e:
    if str(e) == "no such table: receipt_templates": return False
    else: raise e
  return True

def create_database():
  log.info(f"Creating database '{_get_db_connstr()}'")
  (conn, c) = dbh()
  db_install_dir = pathlib.Path(__file__).parent / 'db'
  db_install_files = sorted(db_install_dir.glob('*.sql'))
  for sql_file in db_install_files:
    c.executescript(sql_file.read_text(encoding='UTF-8'))
  conn.commit()

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
  log.warning(f"Dropping database '{_get_db_connstr()}'")
  (conn, c) = dbh()
  if conn:
    close_db()
  pathlib.Path(_get_db_connstr()).unlink()

def _receipt_templates_row_to_dict(row: sqlite3.Row) -> dict:
  return {
    'id':          row[0],
    'type':        row[1],
    'locale_code': row[2],
    'template':    row[3],
  }

def receipt_templates_get(type: str, locale_code: str):
  log.debug(f"receipt_templates_get():> type='{type}', locale_code='{locale_code}'")
  (conn, c) = dbh()
  c.execute('''
  SELECT * FROM receipt_templates WHERE type = ? AND locale_code = ?
  ''', (type, locale_code))
  return _receipt_templates_row_to_dict(c.fetchone())

def receipt_templates_post(template: dict) -> int:
  log.debug(f"receipt_templates_post():> template='{template.__dict__}'")
  (conn, c) = dbh()
  c.execute('''
  INSERT INTO receipt_templates VALUES (?,?,?,?)
  ''', (template.id or None, template.type, template.locale_code, template.template))
  conn.commit()
  return c.lastrowid

def receipt_templates_list():
  (conn, c) = dbh()
  c.execute("SELECT * FROM receipt_templates")
  templates = []
  for t in c.fetchall():
    templates.append(_receipt_templates_row_to_dict(t))
  return templates

def receipt_templates_put(template: dict):
  log.debug(f"receipt_templates_put():> template='{template.__dict__}'")
  (conn, c) = dbh()
  c.execute('''
  UPDATE receipt_templates SET (type, locale_code, template) = (?,?,?) WHERE id = ?
  ''', (template.type, template.locale_code, template.template, template.id))
  conn.commit()
