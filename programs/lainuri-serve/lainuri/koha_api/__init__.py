from lainuri.config import get_config
from lainuri.logging_context import logging
log = logging.getLogger(__name__)
# Save HTTP responses to a scrape-log so we can later inspect what went wrong in the brittle screen scraping components.
log_scrape = logging.getLogger('lainuri.scraping')

from lainuri.constants import Status
import lainuri.exception as exception
import lainuri.exception.ils as exception_ils
import lainuri.locale
import lainuri.status

from bs4 import BeautifulSoup
import bs4
import functools
import json
from pprint import pprint
import re
import time
import traceback
import urllib3
import urllib3.exceptions


class KohaAPI():
  required_permissions = {
    'auth': 'get_session',
    'borrowers': 'view_borrowers',
  #  'catalogue': 'staff_login',
    'circulate': 'circulate_remaining_permissions',
    'editcatalogue': '*',
  }

  sessionid = ''
  koha_baseurl = ''
  current_event_id = ''
  current_request_url = ''

  def __init__(self):
    self.koha_baseurl = get_config('koha.baseurl')
    self.http = urllib3.PoolManager(
      timeout=urllib3.Timeout(connect=get_config('koha.timeout_request_connect_ms')/1000, read=get_config('koha.timeout_request_read_ms')/1000),
      retries=False,
    )

  def _request(self, method, url, headers=None, fields=None, expect_json=1, expect_html=None):
    retries_left = 4
    while retries_left != 0:
      retries_left = retries_left-1
      try:
        r = self.http.request(
          method,
          url,
          fields,
          headers,
        )
        lainuri.status.update_status('ils_connection_status', Status.SUCCESS)

        if expect_html: return self._maybe_not_logged_in(r, self._receive_html(r))
        if expect_json: return self._maybe_not_logged_in(r, self._receive_json(r))

        break # from the retry loop

      except Exception as e:
        log.exception(f"Exception requesting Koha API '{url}'")
        if retries_left == 0:
          raise exception_ils.ILSConnectionFailure(str(e))
        if isinstance(e, urllib3.exceptions.NewConnectionError):
          lainuri.status.update_status('ils_connection_status', Status.ERROR)
          time.sleep(1)
        elif isinstance(e, urllib3.exceptions.ConnectTimeoutError):
          lainuri.status.update_status('ils_connection_status', Status.PENDING)
          time.sleep(1)
        elif isinstance(e, urllib3.exceptions.ReadTimeoutError):
          lainuri.status.update_status('ils_connection_status', Status.PENDING)
          time.sleep(1)
        elif "TRANSPARENT_REAUTHENTICATION" in str(e):
          headers['Cookie'] = f'CGISESSID={self.sessionid}'
          pass # Continue to the next retry loop
        else:
          lainuri.status.update_status('ils_connection_status', Status.ERROR)
          raise e

  def _scrape_log_header(self, r: urllib3.HTTPResponse):
    return f"event_id='{self.current_event_id}' status='{r.status} url='{r.geturl() or self.current_request_url}"

  def _receive_json(self, r: urllib3.HTTPResponse):
    data = r.data.decode('utf-8')
    log_scrape.info(self._scrape_log_header(r) + "\n" + data)
    payload = json.loads(data)
    self._maybe_missing_permission(payload)
    return payload

  def _receive_html(self, r: urllib3.HTTPResponse) -> (BeautifulSoup, list, list):
    data = r.data.decode('utf-8')
    try:
      soup = BeautifulSoup(data, features="html.parser")
      for e in soup.select('script'): e.decompose() # Remove all script-tags
      log_scrape.info(self._scrape_log_header(r) + "\n" + soup.select_one('body').prettify())
    except Exception as e:
      log_scrape.info(f"event_id='{self.current_event_id}'\n" + data)
      log.error(f"Failed to parse HTML for event_id='{self.current_event_id}': {traceback.format_exc()}")
      raise e
    return soup

  def _parse_html(self, soup: BeautifulSoup):
    alerts = soup.select('.dialog.alert')
    # Filter away hidden alerts
    alerts = [m.prettify() for m in alerts if not(m.attrs.get('style')) or not(re.match(r'(?i:display:\s*none)', m.attrs.get('style')))]
    messages = soup.select('.dialog.message')
    # Filter away hidden messages
    messages = [m.prettify() for m in messages if not(m.attrs.get('style')) or not(re.match(r'(?i:display:\s*none)', m.attrs.get('style')))]
    return (alerts, messages)

  def _maybe_not_logged_in(self, r, payload):
    if isinstance(payload, dict) and payload.get('error', None):
      if r.status == 401:
        self._transparent_reauthentication()
    elif isinstance(payload, BeautifulSoup):
      login_error = payload.select("#login_error")
      if login_error:
        self._transparent_reauthentication()
    return (r, payload)

  def _maybe_missing_permission(self, payload):
    if isinstance(payload, dict) and payload.get('error', None):
      if payload.get('required_permissions'):
        lainuri.status.update_status('ils_credentials_status', Status.PENDING)
        raise exception_ils.PermissionMissing(payload.get('required_permissions'))
    lainuri.status.update_status('ils_credentials_status', Status.SUCCESS)

  def _transparent_reauthentication(self):
    self.authenticate()
    raise Exception("TRANSPARENT_REAUTHENTICATION")

  def authenticated(self):
    if not self.sessionid: return 0

    # TODO: Koha API is broken here. On success we get 500, on error we get 401.
    r = self.http.request_encode_body(
      'GET',
      self.koha_baseurl+'/api/v1/auth/session',
      headers = {
        'Cookie': f'CGISESSID={self.sessionid}',
      },
      fields = {
        'sessionid': self.sessionid,
      },
    )
    self._receive_json(r)
    if r.status == 500 or r.status == 200: #Bug in Koha API
      return 1
    else:
      return 0

  def authenticate(self):
    log.info(f"Authenticating")

    r = self.http.request(
      'POST',
      self.koha_baseurl + '/api/v1/auth/session',
      headers = {
        'Cookie': f'CGISESSID={self.sessionid}',
      },
      fields = {
        'password': get_config('koha.password'),
        'userid': get_config('koha.userid'),
      },
    )
    payload = self._receive_json(r)
    error = payload.get('error', None)
    if error:
      lainuri.status.update_status('ils_credentials_status', Status.ERROR)
      if 'Login failed' in error: raise exception_ils.InvalidUser(get_config('koha.userid'))
      else: raise Exception(f"Unknown error '{error}'")
    self.sessionid = payload['sessionid']
    return payload

  def deauthenticate(self):
    if not self.sessionid: return None
    log.info(f"Deauthenticating")
    r = self.http.request_encode_body(
      'DELETE',
      self.koha_baseurl + '/api/v1/auth/session',
      headers = {
        'Cookie': f'CGISESSID={self.sessionid}',
      },
      fields = {
        'sessionid': self.sessionid,
      },
    )
    payload = self._receive_json(r)
    error = payload.get('error', None)
    if error:
      if 'Logout failed' in error: raise exception_ils.InvalidUser(get_config('koha.userid'))
      else: raise Exception(f"Unknown error '{error}'")
    self.sessionid = None
    return payload

  def authenticate_user(self, user_barcode, userid=None, password=None) -> dict:
    log.info(f"Auth user '{user_barcode or userid}'.")
    if password == None:
      borrower = self.get_borrower(user_barcode=user_barcode)
      if borrower:
        return borrower
      else:
        raise exception_ils.InvalidUser(user_barcode)

  @functools.lru_cache(maxsize=get_config('koha.api_memoize_cache_size'), typed=False)
  def get_borrower(self, user_barcode=None, borrowernumber=None):
    self.current_request_url = self.koha_baseurl + f'/api/v1/patrons'
    log.info(f"Get borrower: user_barcode='{user_barcode}' borrowernumber='{borrowernumber}'")

    fields = {}
    if user_barcode: fields['cardnumber'] = user_barcode
    if borrowernumber: fields['borrowernumber'] = borrowernumber

    (response, payload) = self._request(
      'GET',
      self.current_request_url,
      headers = {
        'Cookie': f'CGISESSID={self.sessionid}',
      },
      fields = fields,
    )

    if isinstance(payload, dict) and payload.get('error', None):
      error = payload.get('error', None)
      if error:
        raise Exception(f"Unknown error '{error}'")

    if len(payload) > 1:
      raise Exception(f"Got more than one user with barcode='{user_barcode}'!")
    if len(payload) == 0:
      raise exception_ils.NoUser(user_barcode)

    return payload[0]

  @functools.lru_cache(maxsize=get_config('koha.api_memoize_cache_size'), typed=False)
  def get_item(self, item_barcode):
    self.current_request_url = self.koha_baseurl + f'/api/v1/items'
    log.info(f"Get item: item_barcode='{item_barcode}'")
    (response, payload) = self._request(
      'GET',
      self.current_request_url,
      headers = {
        'Cookie': f'CGISESSID={self.sessionid}',
      },
      fields = {
        'barcode': item_barcode,
      },
    )

    if isinstance(payload, dict) and payload.get('error', None):
      error = payload.get('error', None)
      if error:
        raise Exception(f"Unknown error '{error}'")

    if len(payload) > 1:
      raise Exception(f"Got more than one item with item_barcode='{item_barcode}'!")
    if len(payload) == 0:
      raise exception_ils.NoItem(item_barcode)

    return payload[0]

  @functools.lru_cache(maxsize=get_config('koha.api_memoize_cache_size'), typed=False)
  def get_record(self, biblionumber):
    log.info(f"Get record: biblionumber='{biblionumber}'")
    (response, payload) = self._request(
      'GET',
      self.koha_baseurl + f'/api/v1/records/{biblionumber}',
      headers = {
        'Cookie': f'CGISESSID={self.sessionid}',
      },
    )

    error = payload.get('error', None)
    if error:
      if response.status == 404:
        raise exception.NoResults(biblionumber)
      raise Exception(f"Unknown error '{error}'")
    return payload

  def checkin(self, barcode) -> tuple:
    log.info(f"Checkin: barcode='{barcode}'")
    (response, soup) = self._request(
      'POST',
      self.koha_baseurl + '/cgi-bin/koha/circ/returns.pl?language=en',
      fields={
        'barcode': barcode
      },
      headers = {
        'Cookie': f'CGISESSID={self.sessionid};KohaOpacLanguage=en',
      },
      expect_html=True,
    )

    (alerts, messages) = self._parse_html(soup)

    states = {}
    status = None
    alerts = [a for a in alerts if not self.checkin_has_status(a, states, barcode)]
    messages = [a for a in messages if not self.checkin_has_status(a, states, barcode)]

    # Check if the checkin actually went through in Koha, this is indicated by the #checkedintable contents
    # The alerts and messages don't have a clear status indication of success or failure.
    checked_in_barcode_cells = soup.select('table#checkedintable tr td.ci-barcode') # Thank you Koha for tagging UI elements
    for cell in checked_in_barcode_cells:
      if barcode in str(cell):
        status = Status.SUCCESS
        break
    if not status: status = Status.ERROR

    if (alerts or messages):
      states['unhandled'] = [*(alerts or []), *(messages or [])]
    if states.get('status', None):
      status = states.pop('status')
    log.info(f"Checkin complete: item_barcode='{barcode}' with status='{status}' states='{states}'")
    return (status, states)

  def checkin_has_status(self, message, states, barcode):
    m_not_checked_out = re.compile('Not checked out', re.S | re.M)
    match = m_not_checked_out.search(message)
    if match:
      states['not_checked_out'] = True
      states['status'] = Status.SUCCESS # If the item is not checked out, it wont be registered as a checkin in the table#checkedintable
      return 'not_checked_out'

    m_return_to_another_branch = re.compile('Please return item to: (?P<branchname>.+?)\n', re.S | re.M)
    match = m_return_to_another_branch.search(message)
    if match:
      states['return_to_another_branch'] = match.group('branchname')
      return 'return_to_another_branch'

    m_no_item = re.compile('No item with barcode', re.S | re.M)
    match = m_no_item.search(message)
    if match:
      raise exception_ils.NoItem(barcode)

    m_fines = re.compile('Patron has outstanding fines of (?P<fine_amount>\d+[.,]?\d*)\.')
    match = m_fines.search(message)
    if match:
      states['outstanding_fines'] = match.group('fine_amount')

    return None

  def checkout(self, barcode, borrowernumber) -> tuple:
    log.info(f"Checkout: barcode='{barcode}' borrowernumber='{borrowernumber}'")
    (response, soup) = self._request(
      'POST',
      self.koha_baseurl + '/cgi-bin/koha/circ/circulation.pl?language=en',
      fields={
        'restoreduedatespec': '',
        'barcode': barcode,
        'duedatespec': '',
        'borrowernumber': borrowernumber,
        'branch': get_config('koha.branchcode'),
        'debt_confirmed': 0,
      },
      headers = {
        'Cookie': f'CGISESSID={self.sessionid};KohaOpacLanguage=en',
      },
      expect_html=True,
    )
    (alerts, messages) = self._parse_html(soup)

    states = {}
    status = None
    alerts = [a for a in alerts if not self.checkout_has_status(a, states)]
    messages = [a for a in messages if not self.checkout_has_status(a, states)]

    # Check if the checkout actually went through in Koha, this is possibly indicated by the <div class="lastchecked">
    # The alerts and messages don't have a clear status indication of success or failure.
    lastchecked_elem = soup.select('div.lastchecked')
    for cell in lastchecked_elem:
      if barcode in str(cell):
        status = Status.SUCCESS
        break
    if not status: status = Status.ERROR

    if (alerts or messages):
      states['unhandled'] = [*(alerts or []), *(messages or [])]
    if states.get('status', None):
      status = states.pop('status')
    log.info(f"Checkout complete: item_barcode='{barcode}' borrowernumber='{borrowernumber}' with states='{states}'")
    return (status, states)

  def checkout_has_status(self, message, states):
    m_not_checked_out = re.compile('id="circ_impossible"', re.S | re.M | re.I)
    match = m_not_checked_out.search(message)
    if match:
      states['checkout_impossible'] = True
      states['status'] = Status.ERROR
      return 'not_checked_out'

    m_needsconfirmation = re.compile('id="circ_needsconfirmation"', re.S | re.M | re.I)
    match = m_needsconfirmation.search(message)
    if match:
      states['needs_confirmation'] = True
      states['status'] = Status.ERROR
      return 'needs_confirmation'

    return None

  def receipt(self, borrowernumber, slip_type) -> str:
    log.info(f"Receipt: borrowernumber='{borrowernumber}' slip_type='{slip_type}'")
    if slip_type not in ['qslip','checkinslip']:
      raise TypeError(f"Receipt:> borrowernumber='{borrowernumber}' slip_type='{slip_type}' has invalid slip_type. Allowed values ['qslip','checkinslip']")

    language = lainuri.locale.get_locale(iso639_1=False, iso639_1_iso3166=True)

    (response, soup) = self._request(
      'GET',
      self.koha_baseurl + f'/cgi-bin/koha/members/printslip.pl?borrowernumber={borrowernumber}&print={slip_type}&language={language}',
      headers = {
        'Cookie': f'CGISESSID={self.sessionid};KohaOpacLanguage={language}',
      },
      expect_html=True,
    )

    receipt = soup.select('#receipt')
    if not receipt:
      raise Exception("Fetching the checkout receipt failed: CSS selector '#receipt' didn't match.")
    if receipt: receipt = receipt[0]
    receipt_text = receipt.prettify()
    return receipt_text

  def availability(self, borrowernumber, itemnumber):
    log.info(f"Availability: borrowernumber='{borrowernumber}' itemnumber='{itemnumber}'")
    (response, payload) = self._request(
      'GET',
      self.koha_baseurl + f'/api/v1/availability/item/checkout?itemnumber={itemnumber}&borrowernumber={borrowernumber}',
      headers = {
        'Cookie': f'CGISESSID={self.sessionid}',
      },
    )

    if isinstance(payload, dict) and payload.get('error', None):
      error = payload.get('error', None)
      if error:
        raise Exception(f"Unknown error '{error}'")

    if len(payload) > 1:
      raise Exception(f"Got more than one availability result with borrowernumber='{borrowernumber}' itemnumber='{itemnumber}'!")
    if len(payload) == 0:
      raise Exception(f"Got no availability result with borrowernumber='{borrowernumber}' itemnumber='{itemnumber}'!")

    return payload[0]['availability']

image_types_matcher = re.compile("(?:"+"|.".join(lainuri.config.image_types(True))+"|image)", re.I)
class MARCRecord():
  candidate_author_fields = [['100', 'a'], ['110', 'a']]
  candidate_title_fields  = [['245', 'a'], ['240', 'a']]
  candidate_book_cover_url_fields  = [['856', 'u']]
  candidate_edition_fields = [['250', 'a']]

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
    for field_code, subfield_code in self.candidate_author_fields:
      sf = self.soup.select_one(f'datafield[tag="{field_code}"] subfield[code="{subfield_code}"]')
      if sf: self._author = sf.get_text()
    return self._author

  def book_cover_url(self):
    if self._book_cover_url: return self._book_cover_url
    for field_code, subfield_code in self.candidate_book_cover_url_fields:
      sfs = self.soup.select(f'datafield[tag="{field_code}"] subfield[code="{subfield_code}"]')
      if sfs:
        for sf in sfs:
          if image_types_matcher.search(sf.get_text()):
            self._book_cover_url = sf.get_text()
    return self._book_cover_url

  def edition(self):
    if self._edition: return self._edition
    for field_code, subfield_code in self.candidate_edition_fields:
      sf = self.soup.select_one(f'datafield[tag="{field_code}"] subfield[code="{subfield_code}"]')
      if sf: self._edition = sf.get_text()
    return self._edition

  def title(self):
    if self._title: return self._title
    for field_code, subfield_code in self.candidate_title_fields:
      sf = self.soup.select_one(f'datafield[tag="{field_code}"] subfield[code="{subfield_code}"]')
      if sf: self._title = sf.get_text()
    return self._title

@functools.lru_cache(maxsize=get_config('koha.api_memoize_cache_size'), typed=False)
def get_fleshed_item_record(barcode):
  log.info(f"Get fleshed item record: barcode='{barcode}'")
  try:
    if not barcode: raise exception_ils.NoItemIdentifier()
    item = koha_api.get_item(barcode)
    payload = koha_api.get_record(item['biblionumber'])
    record = MARCRecord(payload)

    return {
      'author': record.author(),
      'title': record.title(),
      'book_cover_url': record.book_cover_url(),
      'edition': record.edition(),
      'item_barcode': barcode,
      'status': Status.SUCCESS,
    }
  except Exception as e:
    return {
      'item_barcode': barcode,
      'status': Status.ERROR,
      'states': {
        'exception': {
          'type': type(e).__name__,
          'trace': traceback.format_exc(),
        },
      },
    }


# TODO: Thread safety for KohaAPI()
koha_api = KohaAPI()
