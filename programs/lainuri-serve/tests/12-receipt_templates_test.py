#!/usr/bin/python3

import context
import context.items
import context.users
import lainuri.db
import lainuri.db.receipt_template as receipt_template
lainuri.db.init()
lainuri.db.create_database()

from lainuri.constants import Status
import lainuri.websocket_server
import lainuri.event
import lainuri.event_queue
import lainuri.printer as lp

import base64
import json
import re
import unittest.mock

def test_list_print_templates(subtests):
  event, resp_event = (None, None)

  with subtests.test("Given a LEPrintTemplateList-event"):
    event = lainuri.event.LEPrintTemplateList()

  with subtests.test("When the event has been handled"):
    assert event == lainuri.event_queue.push_event(event)
    assert lainuri.websocket_server.handle_one_event(5)

  with subtests.test("Then a response event is generated"):
    resp_event = lainuri.websocket_server.handle_one_event(5)
    assert resp_event

  with subtests.test("And the response has a list of all the receipt templates"):
    assert resp_event.states == {}
    assert resp_event.status == Status.SUCCESS
    assert type(resp_event) == lainuri.event.LEPrintTemplateListResponse
    assert len(resp_event.templates) >= 8
    assert len(resp_event.templates) >= 4
    assert resp_event.templates[0] == receipt_template.get(type='checkin', locale_code='en')

def test_save_print_template(subtests):
  event, resp_event = (None, None)

  with subtests.test("Given a LEPrintTemplateSave-event"):
    event = lainuri.event.LEPrintTemplateSave(None, 'checkin', 'nz', 'template contents')

  with subtests.test("When the event has been handled"):
    assert event == lainuri.event_queue.push_event(event)
    assert lainuri.websocket_server.handle_one_event(5)

  with subtests.test("Then a response event is generated"):
    resp_event = lainuri.websocket_server.handle_one_event(5)
    assert resp_event

  with subtests.test("And the response has the new template id"):
    assert resp_event.states == {}
    assert resp_event.status == Status.SUCCESS
    assert type(resp_event) == lainuri.event.LEPrintTemplateSaveResponse
    assert resp_event.id
    assert resp_event.type == event.type
    assert resp_event.locale_code == event.locale_code

  with subtests.test("Given the same LEPrintTemplateSave-event"):
    event = lainuri.event.LEPrintTemplateSave(resp_event.id, 'checkin', 'nz', 'template contents2')

  with subtests.test("When the event has been handled"):
    assert event == lainuri.event_queue.push_event(event)
    assert lainuri.websocket_server.handle_one_event(5)
    resp_event = lainuri.websocket_server.handle_one_event(5)
    assert resp_event

  with subtests.test("Then the response was an UPDATE"):
    assert resp_event.states == {}
    assert resp_event.status == Status.SUCCESS
    assert type(resp_event) == lainuri.event.LEPrintTemplateSaveResponse
    assert resp_event.id == event.id
    assert resp_event.type == event.type
    assert resp_event.locale_code == event.locale_code

  with subtests.test("Given a LEPrintTemplateSave-event with a bad bad Jinja2 template"):
    event = lainuri.event.LEPrintTemplateSave(None, 'checkin', 'sv', 'bad template contents {{ today }')

  with subtests.test("When the event has been handled"):
    assert event == lainuri.event_queue.push_event(event)
    assert lainuri.websocket_server.handle_one_event(5)
    resp_event = lainuri.websocket_server.handle_one_event(5)
    assert resp_event

  with subtests.test("Then the response has the new template id"):
    assert resp_event.states['exception']['type'] == "TemplateSyntaxError"
    assert resp_event.status == Status.ERROR
    assert type(resp_event) == lainuri.event.LEPrintTemplateSaveResponse
    assert resp_event.type == event.type
    assert resp_event.locale_code == event.locale_code

def test_test_printer_template(subtests):
  assert lainuri.event_queue.flush_all()
  lainuri.config.write_config('devices.thermal-printer.enabled', False)
  event, response_event = (None, None)

  with subtests.test("Given a LEPrintTestRequest-event"):
    event = lainuri.event.LEPrintTestRequest(
      template=receipt_template.get(type='checkin', locale_code='en')['template'],
      data=json.dumps({
        "user": context.users.user1,
        "items": context.items.items1,
        "header": "HEADER CONTENTS",
        "footer": "FOOTER CONTENTS",
      }),
      css="""
      font-size: 24px
      """,
      real_print=False)
    lainuri.event_queue.push_event(event)

  with subtests.test("When the LEPrintTestRequest-event is handled"):
    assert lainuri.websocket_server.handle_one_event(5) == event

  with subtests.test("Then a LEPrintTestResponse-event is generated"):
    response_event = lainuri.websocket_server.handle_one_event(5)
    assert type(response_event) == lainuri.event.LEPrintTestResponse
    assert response_event.states == {}
    assert response_event.status == Status.SUCCESS
    assert type(response_event.image) == str
    assert base64.b64decode(response_event.image)

  with subtests.test("And the image-attribute is hidden from log serialization"):
    as_text = response_event.to_string()
    assert re.compile('\'image\': \d+').search(as_text)
