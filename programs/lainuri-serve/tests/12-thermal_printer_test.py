#!/usr/bin/python3

import context

from lainuri.config import get_config
from lainuri.constants import Status
import lainuri.websocket_server
import lainuri.event
import lainuri.event_queue
import lainuri.hs_k33
import lainuri.koha_api
import lainuri.printer as lp
import lainuri.printer.status

from datetime import datetime
import os
import threading
import time
import unittest.mock

poem = """
<body>
  <h4>{{today}} {{header or footer}}</h4>
  <p>
    Johda joelle<br/>
    Juhannus, heilutin<br/>
    "V" mustia joutsenia<br/>
    Edessä toivolla hautaan<br/>
    Koko punaisen syyskuun ajan<br/>
    Taivaalla palo-päällystetty<br/>
    Pyysin sinua esiintymään<br/>
    Kuin piikki pyhille<br/>
  </p><p>
    Külm oli mu hing<br/>
    Sõnatu oli valu<br/>
    Ma seisin silmitsi, kui mu maha jätsid<br/>
    Roos vihmas<br/>
    Nii et ma vandusin su habemenuga<br/>
    See pole kunagi lummatud<br/>
    Kas teie tumedad küüned usku<br/>
    Mind surutakse uuesti läbi mu veenide<br/>
  </p><p>
    Bared on your tomb<br/>
    I am a prayer for your loneliness<br/>
    And would you ever soon<br/>
    Come above unto me?<br/>
    For once upon a time<br/>
    From the binds of your lowliness<br/>
    I could always find<br/>
    The right slot for your sacred key<br/>
  </p><p>
    Шесть футов глубиной является разрез<br/>
    В моем сердце эта безбрачная тюрьма<br/>
    Обесцвечивает все с туннельным зрением<br/>
    Sunsetter<br/>
    Nymphetamine<br/>
    Больной и слабый от моего состояния<br/>
    Эта похоть, вампирская зависимость<br/>
    Ей одной в полном подчинении<br/>
    Не лучше<br/>
    Nymphetamine<br/>
  </p><p>
    苯丙胺，苯丙胺<br/>
    苯丙胺女孩<br/>
    苯丙胺，苯丙胺<br/>
    我的安非他命女孩<br/>
  </p><p>
    محطم بسحرك<br/>
    أنا محاط بدائرة مثل الفريسة<br/>
    العودة في الغابة<br/>
    حيث همسات تقنع<br/>
    المزيد من مسارات السكر<br/>
    وضعت أكثر سيدة بيضاء<br/>
    من أركان الملح<br/>
    حفظ سدوم ليلا في خليج<br/>
  </p><p>
    Paisg gu mo ghàirdeanan<br/>
    Cùm an slighe mesmeric aca<br/>
    Agus dannsa a-mach chun na gealaich<br/>
    Mar a rinn sinn anns na làithean òrail sin<br/>
  </p><p>
    Estrellas de bautizo<br/>
    Recuerdo el camino<br/>
    Éramos aguja y cuchara<br/>
    Extraviados en el heno ardiente<br/>
  </p><p>
    Útilokað í gröfinni þinni<br/>
    Ég er bæn fyrir einmanaleika þínum<br/>
    Og myndir þú alltaf fljótlega<br/>
    Komið hér til mín?<br/>
    Í eitt skipti fyrir<br/>
    Frá bindindum heilagleika þinna<br/>
    Ég gat alltaf fundið<br/>
    Réttur rifa fyrir þinn heilaga lykil<br/>
  </p><p>
    Seks meter dypt er snittet<br/>
    I mitt hjerte, det barløse fengselet<br/>
    Misfarger alt med tunnelsyn<br/>
    Suns<br/>
    Nymphetamine<br/>
    Syk og svak fra tilstanden min<br/>
    Denne lysten, en vampyravhengighet<br/>
    Til henne alene i full underkastelse<br/>
    Ingen bedre<br/>
    Nymphetamine<br/>
  </p><p>
    Մայրամուտ<br/>
    Նիմֆետամին<br/>
    Ոչինչ ավելի լավ<br/>
    Նիմֆետամին<br/>
  </p><p>
    Νυμφεταμίνη, νυμφεταμίνη<br/>
    Νυμφεταμίνη κορίτσι<br/>
    Νυμφεταμίνη, νυμφεταμίνη<br/>
    Η νυμφεταμίνη μου<br/>
  </p>
  <h4>{{footer}}</h4>
</body>
"""

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

def tezt_print_fonts():
  """
  This "test" is used to only print cool receipts to test out fonts and stylings and such.
  DO NOT PRINT these via the thermal printer or you will run out of paper in one go.
  """
  global poem
  for font_family in [
    'initial', 'Bitstream Vera Sans', 'Bitstream Vera Sans Mono', 'Bitstream Vera Serif',
    'DejaVu Sans', 'DejaVu Sans Condensed', 'DejaVu Sans Light', 'DejaVu Sans Mono', 'eufm10',
    'FreeMono', 'FreeSans', 'FreeSerif', 'Gentium', 'Gentium Basic', 'Gentium Book Basic', 'GentiumAlt',
    'Iconsolata', 'Lato', 'Lato Black', 'Lato Hairline', 'Lato Heavy', 'Lato Light', 'Lato Medium', 'Lato Semibold', 'Lato Thin',
    'Liberation Mono', 'Liberation Sans', 'Liberation Sans Narrow', 'Liberation Serif',
    'Noto Mono', 'Noto Sans', 'Noto Sans Display', 'Noto Sans Mono', 'Noto Serif Display',
    'Piboto', 'Piboto Condensed', 'Piboto Light', 'Piboto Thin', 'PibotoLt',
    'Quicksand', 'Quicksand Light', 'Quicksand Medium']:
    assert open(
      os.environ.get('LAINURI_LOG_DIR')+'/receipt.'+font_family.replace(' ', '_')+'.'+datetime.today().isoformat()+'.pdf',
      'wb',
    ).write(
      lp.prepare_weasy_doc(
        lp.render_jinja2_template(receipt_template=poem, items=[], borrower={}, header=None, footer='font-family:'+font_family),
        page_increment=10,
        css_dict={
          'font-family': f"{font_family} !important"
        }
      ).write_pdf()
    )

def test_format_css_rules_from_config():
  assert lp._format_css_rules_from_config() == [
    "body {\n"+\
    "  font-family: Quicksand, sans-serif !important;\n"+\
    "  font-size: 12px;\n"+\
    "}\n"
  ]

def test_print_template_check_in():
  lainuri.config.write_config('devices.thermal-printer.enabled', False)
  global items
  with unittest.mock.patch('lainuri.printer.print_html') as mock_print_html:
    event = lainuri.event.LEPrintRequest(receipt_type='check-in', user_barcode='', items=items)
    printable_sheet = lp.get_sheet(lainuri.config.get_config('devices.thermal-printer.check-in-receipt'), items=event.items, borrower={})
    assert lp.print_html(printable_sheet)

def test_print_koha_check_in_receipt(subtests):
  assert lainuri.event_queue.flush_all()
  lainuri.config.write_config('devices.thermal-printer.enabled', False)
  global items
  with unittest.mock.patch('lainuri.printer.print_html') as mock_print_html:
    with subtests.test("Given the check-in receipt template backend is set to 'koha'"):
      lainuri.config.write_config('devices.thermal-printer.check-in-receipt', 'koha')
    with subtests.test("And the check-in receipt template default borrower is set"):
      lainuri.config.write_config('devices.thermal-printer.check-in-receipt-koha-borrower', 19)

    with subtests.test("When a check-in print request is handled using 'koha' as backend receipt template source"):
      lainuri.websocket_handlers.printer.print_receipt(lainuri.event.LEPrintRequest('check-in', items=[], user_barcode=None))
      assert lainuri.event_queue.history[0].states == {} # Catch a possible exception from handling of the event

    with subtests.test("Then the check-in receipt contains the information from the receipt template default borrower"):
      #TODO: Should intelligently know what is in the test servers check-in template. assert get_config('devices.thermal-printer.check-in-receipt-koha-borrower') in mock_print_html.call_args.args[0]
      assert 'Acevedo' in mock_print_html.call_args[0][0]

def test_printer_status_polling(subtests):
  printer_thr = None

  with unittest.mock.patch('lainuri.hs_k33.HSK_Printer.real_time_transmission_status') as mock_rtts:

    with subtests.test("Given a thermal printer status polling thread"):
      printer_thr = lainuri.printer.status.get_daemon()
      printer_thr.start()

    with subtests.test("When status polling is requested"):
      printer_thr = lainuri.printer.status.start_polling_for_receipt_torn(lainuri.event.LEPrintRequest('check-out', items=[], user_barcode='l-t-u-good'))
      assert printer_thr.is_alive()

    with subtests.test("And a bit of time has passed"):
      time.sleep(1.5)

    with subtests.test("Then status polling is performed"):
      mock_rtts.assert_called_with(printer_status=True)

    with subtests.test("Finally the status polling thread is terminated"):
      lainuri.printer.status.stop_daemon()
      printer_thr.join(5)
      assert not printer_thr.is_alive()

def test_print_koha_api(subtests):
  assert lainuri.event_queue.flush_all()
  lainuri.config.write_config('devices.thermal-printer.enabled', False)
  response_event = None
  lainuri.event_queue.flush_all()
  printer_thr = None

  with subtests.test("SetUp: Assert the receipt is torn away"):
    assert lainuri.hs_k33.get_printer().is_paper_torn_away()

  with subtests.test("SetUp: Given a thermal printer status polling thread"):
    printer_thr = lainuri.printer.status.get_daemon()
    printer_thr.start()
    assert printer_thr.is_alive()

  with subtests.test("Scenario: Print check-out -receipt via Koha API"):
    with subtests.test("Given a check-out print request"):
      event = lainuri.event_queue.push_event(lainuri.event.LEPrintRequest('check-out', items=[], user_barcode='l-t-u-good'))
      assert lainuri.websocket_server.handle_one_event(5) == event

    with subtests.test("When the event is handled"):
      response_event = lainuri.websocket_server.handle_one_event(5)

    with subtests.test("Then the response is a success"):
      assert type(response_event) == lainuri.event.LEPrintResponse
      assert not response_event.states.get('exception', None)
      assert response_event.status == lainuri.event.Status.SUCCESS

    with subtests.test("And the receipt is not torn away"):
      assert not lainuri.hs_k33.get_printer().is_paper_torn_away()

  with subtests.test("Scenario: Print check-in -receipt via Koha API"):
    with subtests.test("Given a check-in print request"):
      event = lainuri.event_queue.push_event(lainuri.event.LEPrintRequest('check-in', items=[], user_barcode=None))
      assert lainuri.websocket_server.handle_one_event(5) == event

    with subtests.test("When the event is handled"):
      response_event = lainuri.websocket_server.handle_one_event(5)

    with subtests.test("Then the response is a success"):
      assert type(response_event) == lainuri.event.LEPrintResponse
      assert not response_event.states.get('exception', None)
      assert response_event.status == lainuri.event.Status.SUCCESS

    with subtests.test("And the receipt is not torn away"):
      assert not lainuri.hs_k33.get_printer().is_paper_torn_away()

  with subtests.test("TearDown: the status polling thread is terminated"):
    lainuri.printer.status.stop_daemon()
    printer_thr.join(5)
    assert not printer_thr.is_alive()

def test_print_exception_bad_cli_command():
  global items
  assert lainuri.event_queue.flush_all()
  return "SKIPPED: Piloting deprecation of CUPS and using ESC/POS raster printing"

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
