#!/usr/bin/python3

import context
from lainuri.config import get_config

import pytest_subtests

import lainuri.websocket_server
import lainuri.event

def test_route_events(subtests):
  event = lainuri.event.LERFIDTagsPresent(tags_present=[])
  lainuri.event_queue.push_event(event)
  assert lainuri.websocket_server.handle_one_event(5) == event

  event = lainuri.event.LEConfigGetpublic()
  lainuri.event_queue.push_event(event)
  assert lainuri.websocket_server.handle_one_event(5) == event
  event_resp = lainuri.websocket_server.handle_one_event(5)
  assert type(event_resp) == lainuri.event.LEConfigGetpublic_Response

