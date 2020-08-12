#!/usr/bin/python3

import context
from lainuri.config import get_config

import pytest_subtests
import unittest.mock

from lainuri.constants import Status
import lainuri.event as le
import lainuri.status
import lainuri.websocket_server


def test_read_master_barcode_and_enter_admin_menu_finally_leave_admin_menu(subtests):
  assert lainuri.event_queue.flush_all()
  event = None
  event_response = None

  with subtests.test("Given Lainuri is in 'get_items'-state"):
    lainuri.status.set_lainuri_state('get_items')

  with subtests.test("When the master barcode is read"):
    lainuri.websocket_server.handle_barcode_read(None, get_config('admin.master-barcode'))

  with subtests.test("Then the Lainuri state is switched to 'admin'"):
    assert lainuri.status.lainuri_state == 'admin'
  with subtests.test("And a LEAdminModeEnter-event is dispatched to the client"):
    event = lainuri.websocket_server.handle_one_event(5)
    assert type(event) == le.LEAdminModeEnter
    assert event.recipient == 'client' or event.recipient is None
    assert event.default_recipient == 'client'
    assert event == lainuri.event_queue.history[0]

  with subtests.test("When the LEAdminModeLeave-event is received"):
    event = le.LEAdminModeLeave()
    lainuri.event_queue.push_event(event)

  with subtests.test("And dispatched"):
    assert lainuri.websocket_server.handle_one_event(5) == event
    assert event == lainuri.event_queue.history[1]

  with subtests.test("Then the Lainuri-state is again 'get_items'"):
    assert lainuri.status.lainuri_state == 'get_items'
