#!/usr/bin/python3

import context

import lainuri.websocket_server
import lainuri.websocket_handlers.printer
import lainuri.event
import lainuri.koha_api
import lainuri.printer as lp

def test_print_template_check_in():
  event = lainuri.event.LEPrintRequest(receipt_type='check-in', user_barcode='', items=[
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
  ])
  printable_sheet = lp.get_sheet_check_in(event.items)
  assert lp.print_html(printable_sheet)

def est_print_koha_api():
  lainuri.koha_api.koha_api.authenticate()

  lainuri.websocket_handlers.printer.print_receipt(
    lainuri.event.LEPrintRequest('check-out', items=[], user_barcode='2600104874')
  )
  response_event = lainuri.websocket_server.events[-1]

  assert type(response_event) == lainuri.event.LEPrintResponse
  assert not response_event.status.get('exception', None)
  assert response_event.status['success']
