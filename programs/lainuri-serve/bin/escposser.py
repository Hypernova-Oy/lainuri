from datetime import datetime
import os
from pprint import pprint

import lainuri
import lainuri.hs_k33
import lainuri.printer

import escpos
import escpos.constants
import escpos.printer
import time
import usb.core
import usb.util


hsk = lainuri.hs_k33.get_printer()
def test_page(arg):
  hsk.set_print_concentration(**arg)
  pprint(hsk.escpos_method('text', str(arg)))
  pprint(hsk.escpos_method('qr', "https://www.hypernova.fi/lainuri-self-checkout-machine/",
                                 native=True,
                                 size=3))
  time.sleep(1)

import pdb; pdb.set_trace()

pprint("is_paper_torn_away(): "+str(hsk.is_paper_torn_away()))
pprint(hsk.real_time_transmission_status(printer_status=True).__dict__)
pprint(hsk.real_time_transmission_status(send_offline_status=True, transmission_error_status=True, transmission_paper_sensor_status=True).__dict__)

printable_sheet = lainuri.printer.print_check_in_receipt(items=[])
time.sleep(2)
#hsk.escpos_printer.image('/tmp/weasy.png', impl=u'graphics')
#time.sleep(1)
#hsk.escpos_printer.image('/tmp/weasy.png', impl=u'bitImageColumn')
#time.sleep(1)

args = {'max_printing_dots': 10, 'heating_time': 80, 'heating_interval': 32}
test_page(args)

"""
hsk.escpos_printer.image('/tmp/weasy.png', high_density_vertical=False, high_density_horizontal=False, impl=u'bitImageRaster')
time.sleep(1)
hsk.escpos_printer.image('/tmp/weasy.png', high_density_vertical=False, high_density_horizontal=False, impl=u'graphics')
time.sleep(1)
hsk.escpos_printer.image('/tmp/weasy.png', high_density_vertical=False, high_density_horizontal=False, impl=u'bitImageColumn')
time.sleep(1)
"""


"""
args = {'max_printing_dots': 128, 'heating_time': 100, 'heating_interval': 40}
test_page(args)
args = {'max_printing_dots': 128, 'heating_time': 120, 'heating_interval': 48}
test_page(args)
args = {'max_printing_dots': 128, 'heating_time': 140, 'heating_interval': 56}
test_page(args)
args = {'max_printing_dots': 128, 'heating_time': 160, 'heating_interval': 64}
test_page(args)

args = {'max_printing_dots': 1, 'heating_time': 80, 'heating_interval': 2}
test_page(args)
args = {'max_printing_dots': 9, 'heating_time': 80, 'heating_interval': 2}
test_page(args)
args = {'max_printing_dots': 18, 'heating_time': 80, 'heating_interval': 2}
test_page(args)
args = {'max_printing_dots': 27, 'heating_time': 80, 'heating_interval': 2}
test_page(args)
args = {'max_printing_dots': 36, 'heating_time': 80, 'heating_interval': 2}
test_page(args)
args = {'max_printing_dots': 45, 'heating_time': 80, 'heating_interval': 2}
test_page(args)
args = {'max_printing_dots': 9, 'heating_time': 20, 'heating_interval': 2}
test_page(args)
args = {'max_printing_dots': 9, 'heating_time': 40, 'heating_interval': 2}
test_page(args)
args = {'max_printing_dots': 9, 'heating_time': 80, 'heating_interval': 2}
test_page(args)
args = {'max_printing_dots': 9, 'heating_time': 160, 'heating_interval': 2}
test_page(args)
args = {'max_printing_dots': 9, 'heating_time': 240, 'heating_interval': 2}
test_page(args)
args = {'max_printing_dots': 9, 'heating_time': 80, 'heating_interval': 1}
test_page(args)
args = {'max_printing_dots': 9, 'heating_time': 80, 'heating_interval': 2}
test_page(args)
args = {'max_printing_dots': 9, 'heating_time': 80, 'heating_interval': 4}
test_page(args)
args = {'max_printing_dots': 9, 'heating_time': 80, 'heating_interval': 16}
test_page(args)
args = {'max_printing_dots': 9, 'heating_time': 80, 'heating_interval': 32}
test_page(args)
args = {'max_printing_dots': 9, 'heating_time': 80, 'heating_interval': 64}
test_page(args)
args = {'max_printing_dots': 9, 'heating_time': 80, 'heating_interval': 128}
test_page(args)
args = {'max_printing_dots': 9, 'heating_time': 80, 'heating_interval': 255}
test_page(args)
"""

#pprint(hsk.escpos_printer.cut())
import pdb; pdb.set_trace()

pprint(hsk.real_time_transmission_status(printer_status=True, send_offline_status=True, transmission_error_status=True, transmission_paper_sensor_status=True).__dict__)
pprint(hsk.transmit_status().__dict__)
pprint(hsk.paper_status())

#pprint(hsk.escpos_printer.text("Hello World\n"))




#pprint("yelow")

hsk.close()

