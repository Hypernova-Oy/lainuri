#!/usr/bin/python3

import context

import lainuri.config
import lainuri.event
import lainuri.event_queue
import lainuri.locale
import lainuri.printer
import lainuri.websocket_server

from datetime import datetime
import locale

def test_all_locales_are_installed():
  assert lainuri.locale.get_missing_locales() == []

def test_set_locale(subtests):
  event = None
  assert lainuri.event_queue.flush_all()

  with subtests.test("Given the current locale is 'en'"):
    lainuri.locale.set_locale('en')
    assert lainuri.locale.get_locale(iso639_1=True) == 'en'
    assert lainuri.locale.get_locale(iso639_1_iso3166=True) == 'en_US'
    assert lainuri.locale.get_locale() == 'en'

  with subtests.test("When a LELocaleSet-event is received"):
    event = lainuri.event.LELocaleSet(locale_code='fi', recipient='server')
    assert lainuri.event_queue.push_event(event) == event
    assert lainuri.websocket_server.handle_one_event(5) == event
    assert event == lainuri.event_queue.history[0]

  with subtests.test("Then the locale has changed"):
    assert lainuri.locale.get_locale(iso639_1=True) == 'fi'
    assert lainuri.locale.get_locale(iso639_1_iso3166=True) == 'fi_FI'
    assert lainuri.locale.get_locale() == 'fi'


def test_print_template_with_locales(subtests):
  items = [
    {
      'title': 'Svengabeibe soittaa taas levyjä',
      'author': 'Matti Meikäläinen ja humppaorkesteri',
      'item_barcode': 'e00401003f382624',
    }
  ]
  en_date = None
  fi_date = None
  printable_sheet = None
  new_locale = None
  sheet_filename = None

  with subtests.test("Given the check-in receipt template backend is set to './templates/check_in.j2'"):
    lainuri.config.write_config('devices.thermal-printer.check-in-receipt', './templates/check_in.j2')
    sheet_filename = lainuri.config.get_config('devices.thermal-printer.check-in-receipt')

  with subtests.test("And locale 'en'"):
    new_locale = lainuri.locale.set_locale('en')
    assert new_locale

  with subtests.test("And the current date"):
    en_date = datetime.today().strftime(locale.nl_langinfo(locale.D_FMT))
    assert en_date

  with subtests.test("When a template is processed"):
    printable_sheet = lainuri.printer.get_sheet(sheet_filename, items=items, borrower={})
    assert printable_sheet

  with subtests.test("Then the date format matches the locale 'en'"):
    assert en_date in printable_sheet

  with subtests.test("Given locale 'fi'"):
    new_locale = lainuri.locale.set_locale('fi')
    assert new_locale

  with subtests.test("And the current date"):
    fi_date = datetime.today().strftime(locale.nl_langinfo(locale.D_FMT))
    assert fi_date

  with subtests.test("When a template is processed"):
    printable_sheet = lainuri.printer.get_sheet(sheet_filename, items=items, borrower={})
    assert printable_sheet

  with subtests.test("Then the date format matches the locale 'fi'"):
    assert fi_date in printable_sheet
    assert en_date not in printable_sheet
