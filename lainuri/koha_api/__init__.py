from lainuri.config import get_config
from lainuri.logging_context import logging
log = logging.getLogger(__name__)
# Save HTTP responses to a scrape-log so we can later inspect what went wrong in the brittle screen scraping components.
log_scrape = logging.getLogger('lainuri.scraping')

from bs4 import BeautifulSoup
import bs4
import functools
import json
from pprint import pprint
import re
import traceback
from urllib3 import PoolManager, HTTPResponse


class KohaAPI():
  required_permissions = {
    'editcatalogue': '*',
    'circulate': 'circulate_remaining_permissions',
    'borrowers': 'view_borrowers',
  #  'catalogue': 'staff_login',
  }

  sessionid = ''
  koha_baseurl = ''
  todo_event_id = 'checkout-koha-123'

  def __init__(self):
    self.koha_baseurl = get_config('koha.baseurl')
    self.http = PoolManager()

  def _scrape_log_header(self, r: HTTPResponse):
    return f"event_id='{self.todo_event_id}' status='{r.status} url='{r.geturl()}"

  def _receive_json(self, r: HTTPResponse):
    data = r.data.decode('utf-8')
    log_scrape.info(self._scrape_log_header(r) + "\n" + data)
    payload = json.loads(data)
    self._maybe_not_logged_in(payload)
    self._maybe_missing_permission(payload)
    return payload

  def _receive_html(self, r: HTTPResponse) -> (BeautifulSoup, list, list):
    data = r.data.decode('utf-8')
    try:
      soup = BeautifulSoup(data, features="html.parser")
      for e in soup.select('script'): e.decompose() # Remove all script-tags
      log_scrape.info(self._scrape_log_header(r) + "\n" + soup.select_one('body').prettify())

      alerts = soup.select('.dialog.alert')
      # Filter away hidden alerts
      alerts = [m for m in alerts if m.attrs.get('style') and not re.match(r'(?i:display:\s*none)', m.attrs.get('style'))]
      messages = soup.select('.dialog.message')
      # Filter away hidden messages
      messages = [m for m in messages if m.attrs.get('style') and not re.match(r'(?i:display:\s*none)', m.attrs.get('style'))]
    except Exception as e:
      log_scrape.info(f"event_id='{self.todo_event_id}'\n" + data)
      log.error(f"Failed to parse HTML for event_id='{self.todo_event_id}': {traceback.format_exc()}")
      raise e

    self._maybe_not_logged_in(soup)
    return (soup, alerts, messages)

  def _maybe_not_logged_in(self, payload):
    reauthenticate = 0
    if isinstance(payload, dict) and payload.get('error'):
      if payload.get('error') == 'Not authenticated':
        reauthenticate = 1
    elif isinstance(payload, BeautifulSoup) and payload.get('error'):
      login_error = payload.select("#login_error")
      if login_error:
        reauthenticate = 1
    if reauthenticate:
      if not self.authenticate():
        raise Exception(f"Lainuri device was not authenticated to Koha and failed to automatically reauthenticate.")

  def _maybe_missing_permission(self, payload):
    if isinstance(payload, dict) and payload.get('error'):
      if payload.get('required_permissions'):
        raise Exception(f"Lainuri device is missing permission '{payload.get('required_permissions')}'. Lainuri needs these permissions to access Koha: '{self.required_permissions}'")

  def _expected_one_list_element(self, l: list, error_msg: str):
    if l and len(l) > 1:
      raise Exception(f"Got more than one result! " + error_msg)
    if not l or len(l) == 0:
      raise Exception(f"Got no results! " + error_msg)
    return l[0]

  def authenticated(self):
    r = self.http.request(
      'GET',
      self.koha_baseurl+'/api/v1/auth/session',
      headers = {
        'Cookie': f'CGISESSID={self.sessionid}',
      }
    )
    self._receive_json(r)
    if r.status == '200':
      return 1
    else:
      return 0

  def authenticate(self):
    r = self.http.request(
      'POST',
      self.koha_baseurl + '/api/v1/auth/session',
      fields = {
        'userid': get_config('koha.userid'),
        'password': get_config('koha.password'),
      },
      headers = {
        'Cookie': f'CGISESSID={self.sessionid}',
      },
    )
    payload = self._receive_json(r)
    self.sessionid = payload['sessionid']
    return payload

  @functools.lru_cache(maxsize=get_config('koha.api_memoize_cache_size'), typed=False)
  def get_borrower(self, cardnumber):
    r = self.http.request(
      'GET',
      self.koha_baseurl + f'/api/v1/patrons?cardnumber={cardnumber}',
      headers = {
        'Cookie': f'CGISESSID={self.sessionid}',
      },
    )
    return self._expected_one_list_element(self._receive_json(r), f"cardnumber='{cardnumber}'")

  @functools.lru_cache(maxsize=get_config('koha.api_memoize_cache_size'), typed=False)
  def get_item(self, barcode):
    r = self.http.request(
      'GET',
      self.koha_baseurl + f'/api/v1/items?barcode={barcode}',
      headers = {
        'Cookie': f'CGISESSID={self.sessionid}',
      },
    )
    return self._expected_one_list_element(self._receive_json(r), f"barcode='{barcode}'")

  @functools.lru_cache(maxsize=get_config('koha.api_memoize_cache_size'), typed=False)
  def get_record(self, biblionumber):
    r = self.http.request(
      'GET',
      self.koha_baseurl + f'/api/v1/records/{biblionumber}',
      headers = {
        'Cookie': f'CGISESSID={self.sessionid}',
      },
    )
    return self._receive_json(r)

  def checkin(self, barcode):
    r = self.http.request(
      'POST',
      self.koha_baseurl + '/cgi-bin/koha/circ/returns.pl',
      fields={
        'barcode': barcode
      },
      headers = {
        'Cookie': f'CGISESSID={self.sessionid}',
      },
    )

    (soup, alerts, messages) = self._receive_html(r)
    if (alerts or messages):
      raise Exception(f"Checkin failed: alerts='{alerts // []}' messages='{messages // []}'")
    return soup

  def checkout(self, barcode, borrowernumber):
    r = self.http.request(
      'POST',
      self.koha_baseurl + '/cgi-bin/koha/circ/circulation.pl',
      fields={
        'restoreduedatespec': '',
        'barcode': barcode,
        'duedatespec': '',
        'borrowernumber': borrowernumber,
        'branch': get_config('koha.branchcode'),
        'debt_confirmed': 0,
      },
      headers = {
        'Cookie': f'CGISESSID={self.sessionid}',
      },
    )
    (soup, alerts, messages) = self._receive_html(r)
    needs_confirmation = soup.select('#circ_needsconfirmation.ul.li')
    if (alerts or messages or needs_confirmation):
      raise Exception(f"Checkin failed: alerts='{alerts // []}' messages='{messages // []}' needs_confirmation='{needs_confirmation}'")
    return soup

  def receipt(self, borrowernumber) -> str:
    prnt = 'qslip'
    r = self.http.request(
      'GET',
      self.koha_baseurl + f'/cgi-bin/koha/members/printslip.pl?borrowernumber={borrowernumber}&print={prnt}',
      headers = {
        'Cookie': f'CGISESSID={self.sessionid}',
      },
    )
    (soup, alerts, messages) = self._receive_html(r)
    if (alerts or messages):
      raise Exception(f"Checkin failed: alerts='{alerts // []}' messages='{messages // []}'")
    receipt = soup.select('#receipt')
    if not receipt:
      raise Exception("Fetching the checkout receipt failed: CSS selector '#receipt' didn't match.")
    if receipt: receipt = receipt[0]
    receipt_text = receipt.get_text()
    return receipt_text


class MARCRecord():
  candidate_author_fields = {'100': ['a'], '110': ['a']}
  candidate_title_fields  = {'245': ['a'], '240': ['a']}
  candidate_book_cover_url_fields  = {'856': ['u']}

  _author = ''
  _title = ''
  _book_cover_url = ''

  def __init__(self, record_xml):
    if isinstance(record_xml, str):
      self.soup = BeautifulSoup(record_xml, "xml")
    else:
      self.soup = BeautifulSoup(record_xml['marcxml'], "xml")

  def author(self):
    if self._author: return self._author
    for field_code in self.candidate_author_fields:
      field = self.soup.select_one(f'datafield[tag="{field_code}"]')
      if field:
        for sf in field.children:
          if isinstance(sf, bs4.element.Tag) and sf.attrs['code'] in self.candidate_author_fields[field_code]:
            self._author = sf
            return self._author

  def title(self):
    if self._title: return self._title
    for field_code in self.candidate_title_fields:
      field = self.soup.select_one(f'datafield[tag="{field_code}"]')
      if field:
        for sf in field.children:
          if isinstance(sf, bs4.element.Tag) and sf.attrs['code'] in self.candidate_title_fields[field_code]:
            self._title = sf
            return self._title

  def book_cover_url(self):
    if self._book_cover_url: return self._book_cover_url
    for field_code in self.candidate_book_cover_url_fields:
      field = self.soup.select_one(f'datafield[tag="{field_code}"]')
      if field:
        for sf in field.children:
          if isinstance(sf, bs4.element.Tag) and sf.attrs['code'] in self.candidate_book_cover_url_fields[field_code]:
            self._book_cover_url = sf
            return self._book_cover_url


# TODO: Thread safety for KohaAPI()
koha_api = KohaAPI()
