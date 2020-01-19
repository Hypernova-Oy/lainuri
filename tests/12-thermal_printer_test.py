#!/usr/bin/python3

import context

import lainuri.printer as lp

def te_print_html():
  html_text = """
  <h4>Hello world today</h4>
  <div>
    This div should be printed quite nicely
  </div>
  <p>
    This paragraph should be printed quite nicely<br/>
    <i>This is in italics</i>
    <i>This is in bold</i>
  </p>
  """
  assert lp.print_html(html_text)

def test_print_koha_api():
  import lainuri.websocket_server
  import lainuri.websocket_handlers.printer
  import lainuri.event
  import lainuri.koha_api

  lainuri.koha_api.koha_api.authenticate()

  lainuri.websocket_handlers.printer.print_receipt(
    lainuri.event.LEPrintRequest(items=[], user_barcode='2600104874')
  )
  response_event = lainuri.websocket_server.events[-1]

  assert type(response_event) == lainuri.event.LEPrintResponse
  assert not response_event.status['exception']
  assert response_event.status['success']
