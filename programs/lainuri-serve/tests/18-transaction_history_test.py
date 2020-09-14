#!/usr/bin/python3

import context
import context.transaction_histories
from lainuri.config import get_config

import lainuri.db.transaction_history
import lainuri.websocket_server
from lainuri.constants import Status
import lainuri.event as le
import lainuri.koha_api
import lainuri.rfid_reader as rfid

import time

def test_transaction_histories_listed(subtests):
  assert lainuri.event_queue.flush_all()
  lainuri.db.transaction_history.clear()

  with subtests.test("Given some transactions"):
    lainuri.db.transaction_history.post(context.transaction_histories.item1)
    lainuri.db.transaction_history.post(context.transaction_histories.item2)
    lainuri.db.transaction_history.post(context.transaction_histories.item3)

  with subtests.test("When LETransactionHistoryRequest is dispatched"):
    event = le.LETransactionHistoryRequest(start_time='1975-01-01 01:15:22', end_time=time.time()+3600)
    lainuri.event_queue.push_event(event)
    assert lainuri.websocket_server.handle_one_event(5) == event
    assert event == lainuri.event_queue.history[0]

  with subtests.test("Then a response event is generated"):
    event = lainuri.websocket_server.handle_one_event(5)
    assert event == lainuri.event_queue.history[1]
    assert type(event) == le.LETransactionHistoryResponse
    assert event.states == {}
    assert event.status == Status.SUCCESS
    context.transaction_histories.assert_item1(event.transactions, 0)
    context.transaction_histories.assert_item2(event.transactions, 1)
    context.transaction_histories.assert_item3(event.transactions, 2)
    assert len(event.transactions) == 3

  with subtests.test("When LETransactionHistoryRequest with a bad timestamp is dispatched"):
    event = le.LETransactionHistoryRequest(start_time='1975-01 asd 01:15:22', end_time=time.time()+3600)
    lainuri.event_queue.push_event(event)
    assert lainuri.websocket_server.handle_one_event(5) == event
    assert event == lainuri.event_queue.history[2]

  with subtests.test("Then a response exception event is generated"):
    event = lainuri.websocket_server.handle_one_event(5)
    assert event == lainuri.event_queue.history[3]
    assert type(event) == le.LETransactionHistoryResponse
    assert event.states['exception']['trace'] == "Invalid isoformat string: '1975-01 asd 01:15:22'"
    assert event.status == Status.ERROR
    assert len(event.transactions) == 0
