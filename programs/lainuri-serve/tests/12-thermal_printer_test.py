#!/usr/bin/python3

import context

from lainuri.constants import Status
import lainuri.websocket_server
import lainuri.event
import lainuri.event_queue
import lainuri.koha_api
import lainuri.printer as lp

from datetime import datetime
import os

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
  assert lp.format_css_rules_from_config() == [
    "body {\n"+\
    "  font-family: Quicksand, sans-serif !important;\n"+\
    "  font-size: 12px;\n"+\
    "}\n"
  ]

def test_print_template_check_in():
  global items
  event = lainuri.event.LEPrintRequest(receipt_type='check-in', user_barcode='', items=items)
  printable_sheet = lp.get_sheet('/templates/check_in.j2', items=event.items, borrower={})
  assert lp.print_html(printable_sheet)

def test_print_koha_api():
  assert lainuri.event_queue.flush_all()

  lainuri.koha_api.koha_api.authenticate()

  event = lainuri.event_queue.push_event(lainuri.event.LEPrintRequest('check-out', items=[], user_barcode='l-t-u-good'))
  assert lainuri.websocket_server.handle_one_event(5) == event

  response_event = lainuri.websocket_server.handle_one_event(5)
  assert type(response_event) == lainuri.event.LEPrintResponse
  assert not response_event.states.get('exception', None)
  assert response_event.status == lainuri.event.Status.SUCCESS

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
