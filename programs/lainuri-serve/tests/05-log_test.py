#!/usr/bin/python3

import context

import lainuri.websocket_server
import lainuri.event

def test_event_log_format(caplog):
  lainuri.websocket_server.handle_one_event(event=lainuri.event.LEServerStatusRequest())
  lainuri.websocket_server.handle_one_event(5)

  caplog_entries = ' '.join([''.join(str(t)) for t in caplog.record_tuples])
  assert 'Handling event' in caplog_entries
  assert 'Message to clients' in caplog_entries
