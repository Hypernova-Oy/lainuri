from lainuri.config import get_config
from lainuri.logging_context import logging
log = logging.getLogger(__name__)
# Save HTTP responses to a scrape-log so we can later inspect what went wrong in the brittle screen scraping components.
log_scrape = logging.getLogger('lainuri.scraping')

from lainuri.exceptions import InvalidPassword, InvalidUser, NoResults

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
  current_event_id = ''
  current_request_url = ''
  reauthenticate_tries = 0

  def __init__(self):
    self.koha_baseurl = get_config('koha.baseurl')
    self.http = PoolManager()

  def _scrape_log_header(self, r: HTTPResponse):
    return f"event_id='{self.current_event_id}' status='{r.status} url='{r.geturl() or self.current_request_url}"

  def _receive_json(self, r: HTTPResponse):
    data = r.data.decode('utf-8')
    log_scrape.info(self._scrape_log_header(r) + "\n" + data)
    payload = json.loads(data)
    self._maybe_not_logged_in(r, payload)
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
      alerts = [m for m in alerts if not(m.attrs.get('style')) or not(re.match(r'(?i:display:\s*none)', m.attrs.get('style')))]
      messages = soup.select('.dialog.message')
      # Filter away hidden messages
      messages = [m for m in messages if not(m.attrs.get('style')) or not(re.match(r'(?i:display:\s*none)', m.attrs.get('style')))]
    except Exception as e:
      log_scrape.info(f"event_id='{self.current_event_id}'\n" + data)
      log.error(f"Failed to parse HTML for event_id='{self.current_event_id}': {traceback.format_exc()}")
      raise e

    self._maybe_not_logged_in(r, soup)
    return (soup, alerts, messages)

  def _maybe_not_logged_in(self, r, payload):
    if isinstance(payload, dict) and payload.get('error', None):
      if r.status == 401:
        self.reauthenticate_tries += 1
    elif isinstance(payload, BeautifulSoup):
      login_error = payload.select("#login_error")
      if login_error:
        self.reauthenticate_tries += 1

    if self.reauthenticate_tries == 2:
      if not self.authenticate():
        self.reauthenticate_tries = 0
        raise Exception(f"Lainuri device was not authenticated to Koha and failed to automatically reauthenticate.")
      self.reauthenticate_tries = 0

  def _maybe_missing_permission(self, payload):
    if isinstance(payload, dict) and payload.get('error', None):
      if payload.get('required_permissions'):
        raise Exception(f"Lainuri device is missing permission '{payload.get('required_permissions')}'. Lainuri needs these permissions to access Koha: '{self.required_permissions}'")

  def _expected_one_list_element(self, l: list, error_msg: str):
    if l and len(l) > 1:
      raise Exception(f"Got more than one result! " + error_msg)
    if not l or len(l) == 0:
      raise NoResults(error_msg)
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
    self.reauthenticate_tries += 1
    r = self._auth_post(userid=get_config('koha.userid'), password=get_config('koha.password'))
    payload = self._receive_json(r)
    error = payload.get('error', None)
    if error:
      if 'Login failed' in error: raise InvalidUser(get_config('koha.userid'))
      else: raise Exception(f"Unknown error '{error}'")
    self.sessionid = payload['sessionid']
    self.reauthenticate_tries = 0
    return payload

  def authenticate_user(self, cardnumber, userid=None, password=None) -> dict:
    if password == None:
      borrower = self.get_borrower(cardnumber=cardnumber)
      if borrower:
        return borrower
      else:
        raise InvalidUser(cardnumber)

  def _auth_post(self, password, userid=None, cardnumber=None):
    if not userid or cardnumber:
      raise Exception("Mandatory parameter 'userid' or 'cardnumber' is missing!")
    fields = {
      'password': get_config('koha.password'),
    }
    if userid: fields['userid'] = userid
    if cardnumber: fields['cardnumber'] = cardnumber

    return self.http.request(
      'POST',
      self.koha_baseurl + '/api/v1/auth/session',
      fields = fields,
      headers = {
        'Cookie': f'CGISESSID={self.sessionid}',
      },
    )

  @functools.lru_cache(maxsize=get_config('koha.api_memoize_cache_size'), typed=False)
  def get_borrower(self, cardnumber):
    r = self.http.request_encode_url(
      'GET',
      self.koha_baseurl + f'/api/v1/patrons',
      headers = {
        'Cookie': f'CGISESSID={self.sessionid}',
      },
      fields = {
        'cardnumber': cardnumber,
      },
    )
    self.current_request_url = self.koha_baseurl + f'/api/v1/patrons'
    payload = self._receive_json(r)
    if isinstance(payload, dict) and payload.get('error', None):
      error = payload.get('error', None)
      if error:
        raise Exception(f"Unknown error '{error}'")
    return self._expected_one_list_element(payload, f"cardnumber='{cardnumber}'")

  @functools.lru_cache(maxsize=get_config('koha.api_memoize_cache_size'), typed=False)
  def get_item(self, barcode):
    r = self.http.request_encode_url(
      'GET',
      self.koha_baseurl + f'/api/v1/items',
      headers = {
        'Cookie': f'CGISESSID={self.sessionid}',
      },
      fields = {
        'barcode': barcode,
      },
    )
    self.current_request_url = self.koha_baseurl + f'/api/v1/items'
    payload = self._receive_json(r)
    if isinstance(payload, dict) and payload.get('error', None):
      error = payload.get('error', None)
      if error:
        raise Exception(f"Unknown error '{error}'")
    return self._expected_one_list_element(payload, f"barcode='{barcode}'")

  @functools.lru_cache(maxsize=get_config('koha.api_memoize_cache_size'), typed=False)
  def get_record(self, biblionumber):
    r = self.http.request(
      'GET',
      self.koha_baseurl + f'/api/v1/records/{biblionumber}',
      headers = {
        'Cookie': f'CGISESSID={self.sessionid}',
      },
    )
    payload = self._receive_json(r)
    error = payload.get('error', None)
    if error:
      if r.status == 404:
        raise NoResults(biblionumber)
      raise Exception(f"Unknown error '{error}'")
    return payload

  def checkin(self, barcode) -> dict:
    """
    Returns dict['status'] == 'failed' on error
    """
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

    statuses = {}
    alerts = [a for a in alerts if not self.checkin_has_status(a.prettify(), statuses)]
    messages = [a for a in messages if not self.checkin_has_status(a.prettify(), statuses)]

    if (alerts or messages):
      statuses['unhandled'] = [*(alerts or []), *(messages or [])]
      statuses['status'] = 'failed'
    if statuses.get('status', None) != 'failed':
      statuses['status'] = 'success'
    log.info(f"Checkin barcode='{barcode}' with statuses='{statuses}'")
    return statuses

  def checkin_has_status(self, message, statuses):
    m_not_checked_out = re.compile('Not checked out', re.S | re.M | re.I)
    match = m_not_checked_out.search(message)
    if match:
      statuses['not_checked_out'] = 1
      return 'not_checked_out'

    m_return_to_another_branch = re.compile('Please return item to: (?P<branchname>.+)\n', re.S | re.M | re.I)
    match = m_return_to_another_branch.search(message)
    if match:
      statuses['return_to_another_branch'] = match.group('branchname')
      return 'return_to_another_branch'

    return None

  def checkout(self, barcode, borrowernumber) -> dict:
    """
    Returns dict['status'] == 'failed' on error
    """
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

    statuses = {}
    alerts = [a for a in alerts if not self.checkout_has_status(a.prettify(), statuses)]
    messages = [a for a in messages if not self.checkout_has_status(a.prettify(), statuses)]

    if (alerts or messages):
      statuses['unhandled'] = [*(alerts or []), *(messages or [])]
      statuses['status'] = 'failed'
    if statuses.get('status', None) != 'failed':
      statuses['status'] = 'success'
    log.info(f"Checkout barcode='{barcode}' borrowernumber='{borrowernumber}' with statuses='{statuses}'")
    return statuses

  def checkout_has_status(self, message, statuses):
    m_not_checked_out = re.compile('Not checked out', re.S | re.M | re.I)
    match = m_not_checked_out.search(message)
    if match:
      statuses['not_checked_out'] = 1
      return 'not_checked_out'

    m_needsconfirmation = re.compile('circ_needsconfirmation', re.S | re.M | re.I)
    match = m_needsconfirmation.search(message)
    if match:
      statuses['needs_confirmation'] = 1
      statuses['status'] = 'failed'
      return 'needs_confirmation'

    return None


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
  candidate_edition_fields = {'250': ['a']}

  _author = ''
  _title = ''
  _book_cover_url = ''
  _edition = ''

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
            self._author = sf.get_text()
            return self._author

  def title(self):
    if self._title: return self._title
    for field_code in self.candidate_title_fields:
      field = self.soup.select_one(f'datafield[tag="{field_code}"]')
      if field:
        for sf in field.children:
          if isinstance(sf, bs4.element.Tag) and sf.attrs['code'] in self.candidate_title_fields[field_code]:
            self._title = sf.get_text()
            return self._title

  def book_cover_url(self):
    if self._book_cover_url: return self._book_cover_url
    for field_code in self.candidate_book_cover_url_fields:
      field = self.soup.select_one(f'datafield[tag="{field_code}"]')
      if field:
        for sf in field.children:
          if isinstance(sf, bs4.element.Tag) and sf.attrs['code'] in self.candidate_book_cover_url_fields[field_code]:
            self._book_cover_url = sf.get_text()
            return self._book_cover_url

  def edition(self):
    if self._edition: return self._edition
    for field_code in self.candidate_edition_fields:
      field = self.soup.select_one(f'datafield[tag="{field_code}"]')
      if field:
        for sf in field.children:
          if isinstance(sf, bs4.element.Tag) and sf.attrs['code'] in self.candidate_edition_fields[field_code]:
            self._author = sf.get_text()
            return self._author


@functools.lru_cache(maxsize=get_config('koha.api_memoize_cache_size'), typed=False)
def get_fleshed_item_record(barcode):
  exception = None
  try:
    item = koha_api.get_item(barcode)
    payload = koha_api.get_record(item['biblionumber'])
    record = MARCRecord(payload)

    return {
      'author': record.author(),
      'title': record.title(),
      'book_cover_url': record.book_cover_url(),
      'edition': record.edition(),
      'barcode': barcode,
    }
  except Exception as e:
    exception = {
      'type': str(type(e)),
      'message': str(e),
      'trace': traceback.format_exc(),
    }

  return {
    'barcode': barcode,
    'exception': exception,
  }


# TODO: Thread safety for KohaAPI()
koha_api = KohaAPI()
