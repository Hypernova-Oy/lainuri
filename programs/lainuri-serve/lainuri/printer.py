from lainuri.config import get_config
from lainuri.logging_context import logging
log = logging.getLogger(__name__)

from jinja2 import Template
from datetime import datetime
import os
import traceback
from weasyprint import HTML, CSS
import subprocess

cli_print_command = ['lp', '-']

def print_html(html_text: str):
  log.debug(f"print_html text='{html_text}'")
  if get_config('devices.thermal-printer.enabled') != True:
    log.info(f"Thermal printer disabled by configuration")
    return 1

  weasy_html = HTML(string=html_text)

  pages = 100
  heigth = 25 # Keep looping to find the correct page size to fit all the content
  while pages != 1:
    css = CSS(string=' \
      body {\
        width: 72mm;\
        font-size: '+(get_config('devices.thermal-printer.font-size') or '12px')+';\
      }\
      @page {\
        size: 72mm '+str(heigth)+'mm;\
        margin: 0px;\
      }\
    ')
    doc = weasy_html.render(
      stylesheets=[css],
      enable_hinting = True,
      presentational_hints = True,
    )
    pages = len(doc.pages)
    heigth = heigth + 15

  log.debug(f"print_html pages='{len(doc.pages)}', page0='{doc.pages and doc.pages[0].__dict__}'")

  print_thermal_receipt(doc.write_pdf())

  return 1

def print_thermal_receipt(byttes: bytes):
  global cli_print_command
  ## Save to log the receipt document
  open(
    os.environ.get('LAINURI_LOG_DIR')+'receipt'+datetime.today().isoformat()+'.pdf',
    'wb',
  ).write(byttes)

  ## Invoke system CUPS printer
  if get_config('devices.thermal-printer.enabled'):
    process = subprocess.Popen(cli_print_command, stdout=subprocess.PIPE, stdin=subprocess.PIPE, stderr=subprocess.PIPE)
    process.communicate(input=byttes, timeout=20)
    if process.returncode != 0:
      raise Exception(f"Program exit code not 0. exit='{process.returncode}', stderr='{process.stderr}', stdout='{process.stdout}', command='{cli_print_command}'")

  else:
    log.info(f"Thermal printer is disabled from configuration.")

def get_sheet_check_in(items: list) -> str:
  template = open(
    os.environ.get('LAINURI_CONF_DIR')+'/templates/check_in.j2',
    'r',
  ).read()
  tm = Template(template)

  return tm.render(
    items=items,
    today=datetime.today().strftime(get_config('dateformat'))
  )
