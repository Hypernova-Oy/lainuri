from lainuri.config import get_config
from lainuri.logging_context import logging
log = logging.getLogger(__name__)

from datetime import datetime
import locale
import os
import subprocess

def verify_locales_installed():
  locale_codes = get_config('i18n.enabled_locales')
  missing_locales = get_missing_locales(locale_codes)
  if len(missing_locales) > 0:
    log.error(f"verify_locales_installed():> Found missing locales '{missing_locales}'. Installing them for you.")
    for missing_locale in missing_locales:
      enable_locale(missing_locale)
    install_locales(missing_locales)

def get_missing_locales(locale_codes: list = None):
  if not locale_codes: locale_codes = get_config('i18n.enabled_locales')
  installed_locales = {l.replace('utf8', 'UTF-8'):True for l in subprocess.run(['localectl','list-locales'], capture_output=True, check=True).stdout.decode('UTF-8').split("\n")}
  missing_locales = []

  for lo in locale_codes:
    lo_norm = normalize_2_char_to_POSIX(lo)
    if not installed_locales.get(lo_norm, None):
      missing_locales.append(lo)
  return missing_locales

def enable_locale(locale_code):
  lo_norm = normalize_2_char_to_POSIX(locale_code)
  os.system(f'echo "{lo_norm} UTF-8" >> /etc/locale.gen')
  log.info(f"enable_locale():> Enabled locale '{locale_code}'=>'{lo_norm}'")

def install_locales(locale_codes):
  return subprocess.run(['locale-gen'], check=True)

def set_locale(locale_code):
  locale_code_normalized = normalize_2_char_to_POSIX(locale_code)
  current_locale = locale.getlocale()
  log.debug(f"Setting locale '{current_locale}' to '{locale_code}'=>'{locale_code_normalized}'")
  new_locale = locale.setlocale(category=locale.LC_ALL, locale=locale_code_normalized)
  log.info(f"New locale '{new_locale}' set. From locale '{current_locale}' as '{locale_code}'=>'{locale_code_normalized}'")
  return new_locale

def get_locale(iso639_1: bool = False, iso639_1_iso3166: bool = False):
  if iso639_1_iso3166: return locale.getlocale(locale.LC_ALL)[0][0:5]
  elif iso639_1:       return locale.getlocale(locale.LC_ALL)[0][0:2]
  else:                return locale.getlocale(locale.LC_ALL)[0][0:2]

def normalize_2_char_to_POSIX(locale_2_char) -> str:
  return locale.normalize(locale_2_char+'.UTF-8')

def today():
  return datetime.today().strftime(locale.nl_langinfo(locale.D_FMT) + ' ' + locale.nl_langinfo(locale.T_FMT))
