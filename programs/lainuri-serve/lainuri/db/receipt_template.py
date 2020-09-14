from lainuri.config import get_config, get_lainuri_conf_dir, log_dir
from lainuri.logging_context import logging
log = logging.getLogger(__name__)

from lainuri.db import dbh

import sqlite3

def _receipt_templates_row_to_dict(row: sqlite3.Row) -> dict:
  return {
    'id':          row[0],
    'type':        row[1],
    'locale_code': row[2],
    'template':    row[3],
  }

def get(type: str, locale_code: str):
  log.debug(f"get():> type='{type}', locale_code='{locale_code}'")
  (conn, c) = dbh()
  c.execute('''
  SELECT * FROM receipt_templates WHERE type = ? AND locale_code = ?
  ''', (type, locale_code))
  return _receipt_templates_row_to_dict(c.fetchone())

def post(template: dict) -> int:
  log.debug(f"post():> template='{template.__dict__}'")
  (conn, c) = dbh()
  c.execute('''
  INSERT INTO receipt_templates VALUES (?,?,?,?)
  ''', (template.id or None, template.type, template.locale_code, template.template))
  conn.commit()
  return c.lastrowid

def list_all():
  (conn, c) = dbh()
  c.execute("SELECT * FROM receipt_templates")
  templates = []
  for t in c.fetchall():
    templates.append(_receipt_templates_row_to_dict(t))
  return templates

def put(template: dict):
  log.debug(f"put():> template='{template.__dict__}'")
  (conn, c) = dbh()
  c.execute('''
  UPDATE receipt_templates SET (type, locale_code, template) = (?,?,?) WHERE id = ?
  ''', (template.type, template.locale_code, template.template, template.id))
  conn.commit()
