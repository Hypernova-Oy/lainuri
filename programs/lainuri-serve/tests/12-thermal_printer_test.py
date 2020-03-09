#!/usr/bin/python3

import context

from lainuri.constants import Status
import lainuri.websocket_server
import lainuri.event
import lainuri.event_queue
import lainuri.koha_api
import lainuri.printer as lp

items = [
  {
    'title': 'Titteli 12 mestari',
    'author': 'Matti Meikäläinen',
    'item_barcode': '167N01010101',
  },
  {
    'title': 'Huone 105',
    'author': 'Matti Meikäläinen',
    'item_barcode': '167N21212121',
  },
  {
    'title': 'Svengabeibe soittaa taas levyjä',
    'author': 'Matti Meikäläinen ja humppaorkesteri',
    'item_barcode': 'e00401003f382624',
  }
]

def test_print_template_check_in():
  global items
  event = lainuri.event.LEPrintRequest(receipt_type='check-in', user_barcode='', items=items)
  printable_sheet = lp.get_sheet_check_in(event.items)
  assert lp.print_html(printable_sheet)

def test_print_koha_api():
  assert lainuri.event_queue.flush_all()

  lainuri.koha_api.koha_api.authenticate()

  event = lainuri.event_queue.push_event(lainuri.event.LEPrintRequest('check-out', items=[], user_barcode='l-t-u-good'))
  assert lainuri.websocket_server.handle_one_event(5) == event

  response_event = lainuri.websocket_server.handle_one_event(5)
  assert type(response_event) == lainuri.event.LEPrintResponse
  assert response_event.status == lainuri.event.Status.SUCCESS
  assert not response_event.states.get('exception', None)

def test_print_exception_bad_cli_command():
  global items
  assert lainuri.event_queue.flush_all()

  lainuri_printer_cli_print_command_old = lainuri.printer.cli_print_command
  lainuri.printer.cli_print_command = ['lp-not-exists']

  event = lainuri.event_queue.push_event(
    lainuri.event.LEPrintRequest(receipt_type='check-in', user_barcode='', items=items)
  )
  assert lainuri.websocket_server.handle_one_event(5) == event
  assert lainuri.event_queue.history[0] == event

  response_event = lainuri.websocket_server.handle_one_event(5)
  assert lainuri.event_queue.history[1] == response_event
  assert response_event.status == Status.ERROR
  assert response_event.states['exception']['type'] == 'FileNotFoundError'

  lainuri.printer.cli_print_command = lainuri_printer_cli_print_command_old
