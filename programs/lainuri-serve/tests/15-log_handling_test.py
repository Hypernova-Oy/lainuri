#!/usr/bin/python3

import context
from lainuri.config import get_config
from lainuri.logging_context import logging

from lainuri.constants import Status
import lainuri.event
import lainuri.websocket_handlers.logging
import lainuri.websocket_server

import os
import tailer

log_path = os.environ.get('LAINURI_LOG_DIR')+'/external.log'

def test_write_to_external_log():
  global log_path
  log = logging.getLogger('lainuri.websocket_handlers.logging_external')
  log.fatal('TEST: This is a test message')
  assert 'TEST: This is a test message' in tailer.tail(open(log_path),lines=1)[-1]

def test_handle_external_logging_event(subtests):
  global log_path
  event = None

  assert lainuri.event_queue.flush_all()

  with subtests.test("Given a LELogSend-event from a connected client"):
    event = lainuri.event.LELogSend(
      level='FATAL',
      logger_name='logger.name',
      milliseconds=1281296419264,
      log_entry='this is a test log entry',
    )
    assert event == lainuri.event_queue.push_event(event)
    assert type(lainuri.event_queue.history[0]) == lainuri.event.LELogSend

  with subtests.test("when the event is handled"):
    assert lainuri.websocket_server.handle_one_event(5) == event

  with subtests.test("Then a response is NOT generated"):
    response_event = lainuri.event_queue.history[1]
    assert response_event == None
    # Responding for all log events is too expensive, Raspberry is running out of juice.
    #assert type(response_event) == lainuri.event.LELogReceived
    #assert response_event.states == {}
    #assert response_event.status == Status.SUCCESS

  with subtests.test("And an external log is written"):
    assert 'this is a test log entry' in tailer.tail(open(log_path),lines=1)[-1]
