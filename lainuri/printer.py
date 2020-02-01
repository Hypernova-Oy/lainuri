from lainuri.config import get_config
from lainuri.logging_context import logging
log = logging.getLogger(__name__)

from datetime import datetime
import os
from weasyprint import HTML, CSS
import subprocess

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

  open(
    os.environ.get('LAINURI_LOG_DIR')+'receipt'+datetime.today().isoformat()+'.pdf',
    #os.environ.get('LAINURI_LOG_DIR')+'receipt'+'.pdf',
    'wb',
  ).write(doc.write_pdf())

  if get_config('devices.thermal-printer.enabled'):
    process = subprocess.Popen(['lp', '-'], stdout=subprocess.PIPE, stdin=subprocess.PIPE, stderr=subprocess.PIPE)
    process.communicate(input=doc.write_pdf(), timeout=20)

    if process.returncode != 0:
      raise Exception(f"Failed to print receipt! lp-command exit='{process.returncode}', stderr='{process.stderr}', stdout='{process.stdout}'")
  else:
    log.info(f"Thermal printer is disabled from configuration.")

  return 1
