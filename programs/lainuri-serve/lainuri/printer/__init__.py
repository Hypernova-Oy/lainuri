from lainuri.config import get_config, get_lainuri_conf_dir, log_dir
from lainuri.logging_context import logging
log = logging.getLogger(__name__)

import lainuri.db
from lainuri.constants import Status
import lainuri.hs_k33
from lainuri.koha_api import koha_api
import lainuri.locale
import lainuri.status
from lainuri.printer.printjob import PrintJob

import jinja2
from datetime import datetime
import os
import pathlib
import re
import subprocess
import time
import traceback
import weasyprint

cli_print_command = ['lp', '-']

def list_templates():
  return lainuri.db.receipt_templates_list()

def test_print(pj: PrintJob, real_print: bool = False) -> PrintJob:
  _render_jinja2_template(pj)
  _generate_receipt_png(
    _prepare_weasy_doc(pj),
    pj)
  if real_print: _print_thermal_receipt(doc, pj)
  return pj

def save_template(template: dict):
  jinja2.Environment().parse(source=template.template) #validate template
  if not getattr(template, 'id', None):
    t_id = lainuri.db.receipt_templates_post(template)
    template.id = t_id
  else: lainuri.db.receipt_templates_put(template)

def print_check_out_receipt(pj: PrintJob):
  pj._template_backend = get_config('devices.thermal-printer.check-out-receipt')

  if pj._template_backend == 'koha':
    pj._printable_html = koha_api.receipt(pj.data['user']['borrowernumber'], 'qslip')
  else:
    get_sheet(pj)

  print_html(pj)
  return pj

def print_check_in_receipt(pj: PrintJob):
  get_sheet(pj)
  print_html(pj)
  return pj

def print_html(pj: PrintJob):
  log.debug(f"print_html PrintJob={pj.__dict__}")
  try:
    _print_thermal_receipt(
      _prepare_weasy_doc(pj),
      pj
    )
    lainuri.status.update_status('thermal_printer_status', Status.SUCCESS)
  except Exception as e:
    lainuri.status.update_status('thermal_printer_status', Status.ERROR)
    raise e
  return 1

def get_sheet(pj: PrintJob) -> str:
  try:
    pj._receipt_template = lainuri.db.receipt_templates_get(pj._type, lainuri.locale.get_locale())['template']
  except Exception as e:
    raise type(e)(e, f"Exception when get_sheet():> PrintJob={pj.__dict__}")
  _render_jinja2_template(pj)
  return pj._printable_html

def get_template_filename(template_type: str, locale_code: str) -> pathlib.Path:
  return (get_lainuri_conf_dir() / 'templates' / f"{template_type}-{locale_code}.j2")

def _prepare_weasy_doc(pj: PrintJob) -> weasyprint.Document:
  doc = None
  start_time = time.time()

  weasy_html = weasyprint.HTML(string=pj._printable_html)

  pages = 256
  heigth = 20 # Keep looping to find the correct page size to fit all the content
  while pages != 1:
    pj._page_size_lookups += 1
    default_css = weasyprint.CSS(string=' \
      body {\
        width: 72mm;\
        font-size: 12px;\
        margin: 0px;\
        padding: 0px;\
      }\
      @page {\
        size: 72mm '+str(heigth)+'mm;\
        margin: 0px;\
        padding: 0px;\
      }\
    ')
    doc = weasy_html.render(
      stylesheets=[default_css, *[weasyprint.CSS(string=css) for css in _format_css_rules_from_config(pj.css)]],
      enable_hinting = True,
      presentational_hints = True,
    )
    pages = len(doc.pages)

    # Simple heuristics to quickly detect the proper document length
    old_height = heigth
    if pj._page_size_lookups == 1: heigth = heigth * (pages*0.9 if pages > 2 else pages)
    else: heigth = heigth + (pj._page_increment * (pages-1))
    log.debug(f"Sampling to fit content on one document: i='{pj._page_size_lookups}', old_height='{old_height}', pages='{pages}', new height='{heigth}'")

  end_time = time.time()
  pj._run_time = end_time - start_time
  log.info(f"print_html():> pages='{len(doc.pages)}', page_increment='{pj._page_increment}px', html processing runtime='{pj._run_time}s' iterations='{pj._page_size_lookups}' page0='{doc.pages and doc.pages[0].__dict__}'")
  return doc

def _format_css_rules_from_config(css: str = None):
  css_dict = get_config('devices.thermal-printer.css')

  css_dict_str = "body {\n"
  for css_directive, value in css_dict.items():
    if value[-1] != ';': value += ';'
    css_dict_str += f"  {css_directive}: {value}\n"
  css_dict_str += "}\n"

  css_string = get_config('devices.thermal-printer.css_string')
  return [stylesheet for stylesheet in [css_dict_str, css_string, css] if stylesheet]

def _print_thermal_receipt(doc: weasyprint.Document, pj: PrintJob):
  #TODO: Piloting ESC/POS raster image printing instead of using the rather slow and cumbersome CUPS. Using CUPS with ESC/POS might be impossible due to USB device congestion issues
  return _print_via_escpos_raster(_generate_receipt_png(doc, pj))
  #if (get_config('devices.thermal-printer.cups')):
  #  _print_via_cups(doc.to_pdf())

def _generate_receipt_png(doc: weasyprint.Document, pj: PrintJob):
  pj._png_file_path = log_dir() / f"receipt.{datetime.today().isoformat()}.{pj._type}.png"
  doc.write_png(target=str(pj._png_file_path), resolution=203) # HS-K33 manual states the resolution to be 203 DPI
  return pj._png_file_path

def _print_via_escpos_raster(png_file_path: str):
  if get_config('devices.thermal-printer.enabled'):
    printer = lainuri.hs_k33.get_printer()
    with printer.transaction_lock:
      try:
        printer.print_image(png_file_path)
      finally:
        time.sleep(0.25)
        #printer.send_real_time_request(recover_by_clearing=True) #TODO: Clear a stuck print buffer
        #printer.initialize_printer() #TODO: Clear a stuck print buffer, sample with reading the usb buffer empty first in printer.print_image().
        printer.paper_cut()
        time.sleep(1)  # Give time for the printer to process the image before releasing the lock, otherwise the status polling thread could/might break printing.
    update_paper_status()
  else:
    log.info(f"Thermal printer is disabled from configuration.")

def update_paper_status():
  printer = lainuri.hs_k33.get_printer()
  ps = printer.paper_status()
  if ps == 2: lainuri.status.update_status('thermal_printer_paper_status', Status.SUCCESS)
  if ps == 1: lainuri.status.update_status('thermal_printer_paper_status', Status.PENDING)
  if ps == 0: lainuri.status.update_status('thermal_printer_paper_status', Status.ERROR)

def _print_via_cups(byttes: bytes):
  global cli_print_command

  ## Invoke system CUPS printer
  if get_config('devices.thermal-printer.enabled'):
    process = subprocess.Popen(cli_print_command, stdout=subprocess.PIPE, stdin=subprocess.PIPE, stderr=subprocess.PIPE)
    process.communicate(input=byttes, timeout=20)
    if process.returncode != 0:
      raise Exception(f"Program exit code not 0. exit='{process.returncode}', stderr='{process.stderr}', stdout='{process.stdout}', command='{cli_print_command}'")

  else:
    log.info(f"Thermal printer is disabled from configuration.")

def _render_jinja2_template(pj: PrintJob):
  if not getattr(pj.data, 'today', None): pj.data['today'] = lainuri.locale.today()
  pj._printable_html = jinja2.Template(pj._receipt_template).render(**pj.data)
  return pj._printable_html
