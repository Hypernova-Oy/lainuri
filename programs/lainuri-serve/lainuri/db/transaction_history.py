from lainuri.config import get_config, get_lainuri_conf_dir, log_dir
from lainuri.logging_context import logging
log = logging.getLogger(__name__)

import sqlite3
import time

from lainuri.db import dbh

def _transaction_history_row_to_dict(row: sqlite3.Row) -> dict:
  return {
    'id': row[0], 'transaction_type': row[1], 'transaction_date': row[2],
    'borrower_barcode': row[3],
    'item_barcode': row[4]
  }

def clear():
  log.debug(f"clear():>")
  (conn, c) = dbh()
  c.execute("DELETE FROM transaction_history")
  return c.rowcount

def get_for_borrower(borrower_barcode: str, transaction_date_start=time.time()-10, transaction_date_end=time.time()+10, transaction_types=['checkin','checkout']):
  log.debug(f"get_for_borrower():> borrower_barcode='{borrower_barcode}', transaction_date_start='{transaction_date_start}', transaction_date_end='{transaction_date_end}', transaction_types='{transaction_types}'")
  transaction_date_start = _cast_date(transaction_date_start)
  transaction_date_end   = _cast_date(transaction_date_end)
  (conn, c) = dbh()

  t_types = '"' + '","'.join(transaction_types) + '"'
  c.execute(
    f"SELECT * FROM transaction_history WHERE borrower_barcode = ? AND transaction_date BETWEEN ? AND ? AND transaction_type IN ({t_types});",
    (borrower_barcode, transaction_date_start, transaction_date_end)
  )

  return [_transaction_history_row_to_dict(t) for t in c.fetchall()]

def list_between(transaction_date_start=time.time()-10, transaction_date_end=time.time()+10, transaction_types=['checkin','checkout']):
  log.debug(f"list_between():> transaction_date_start='{transaction_date_start}', transaction_date_end='{transaction_date_end}', transaction_types='{transaction_types}'")
  transaction_date_start = _cast_date(transaction_date_start)
  transaction_date_end   = _cast_date(transaction_date_end)
  (conn, c) = dbh()

  t_types = '"' + '","'.join(transaction_types) + '"'
  c.execute(
    f"SELECT * FROM transaction_history WHERE transaction_date BETWEEN ? AND ? AND transaction_type IN ({t_types});",
    (transaction_date_start, transaction_date_end)
  )

  return [_transaction_history_row_to_dict(t) for t in c.fetchall()]

def post(t: dict) -> int:
  log.debug(f"post():> t='{t}'")
  transaction_date = (t.get('transaction_date', None) and _cast_date(t['transaction_date'])) or time.time()
  (conn, c) = dbh()
  c.execute('''
  INSERT INTO transaction_history (
    id, transaction_type, transaction_date,
    borrower_barcode,
    item_barcode
  ) VALUES (
    ?,?,?,
    ?,
    ?
  )
  ''', (
    t.get('id', None), t['transaction_type'], transaction_date,
    t['borrower_barcode'],
    t['item_barcode'],
  ))
  conn.commit()
  return c.lastrowid


def _cast_date(datesomething):
  import datetime
  import re
  date_seconds = None
  if type(datesomething) == datetime.datetime:
    date_seconds = datesomething.timestamp()
  elif type(datesomething) == int or type(datesomething) == float or re.compile("^\d+\.?\d*$").match(datesomething):
    date_seconds = int(datesomething)
  else:
    date_seconds = datetime.datetime.fromisoformat(datesomething).timestamp()
  return date_seconds
