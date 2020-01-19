from lainuri.logging_context import logging
log = logging.getLogger(__name__)

from weasyprint import HTML, CSS
import subprocess

def print_html(html_text: str):
  log.debug(f"print_html text='{html_text}'")
  weasy_html = HTML(string=html_text)
  css = CSS(string='body { width: 72mm; } @page { size: 72mm; margin: 0px; }')
  doc = weasy_html.render(
    stylesheets=[css],
    enable_hinting = True,
    presentational_hints = True,
  )
  log.debug(f"print_html pages='{len(doc.pages)}', page0='{doc.pages and doc.pages[0].__dict__}'")

  process = subprocess.Popen(['lp', '-'], stdout=subprocess.PIPE, stdin=subprocess.PIPE, stderr=subprocess.PIPE)
  process.communicate(input=doc.write_pdf(), timeout=20)
  return process
