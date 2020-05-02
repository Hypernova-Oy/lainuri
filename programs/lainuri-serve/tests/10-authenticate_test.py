#!/usr/bin/python3

import context
import lainuri.config

from lainuri.exception import NoResults
import lainuri.exception.ils as exception_ils
from lainuri.koha_api import koha_api, MARCRecord, get_fleshed_item_record

borrower = None

def test_authenticate(subtests):
  global borrower

  with subtests.test("Given Lainuri is unauthenticated"):
    koha_api.sessionid = None
    assert koha_api.authenticated() == 0

  with subtests.test("When authentication is attempted with bad credentials"):
    lainuri.config.write_config('koha.userid', 'l-t-dev-bad')
    lainuri.config.write_config('koha.password', 'bad_pass')

  with subtests.test("Then authentication fails"):
    context.assert_raises('Testing bad authentication', exception_ils.InvalidUser, 'l-t-dev-bad',
      lambda: koha_api.authenticate()
    )

  with subtests.test("When authentication is attempted with good credentials"):
    lainuri.config.write_config('koha.userid', 'l-t-dev-good')
    lainuri.config.write_config('koha.password', 'correct_credentials_password-!')

  with subtests.test("Then authentication succeeds"):
    borrower = koha_api.authenticate()
    assert borrower
    assert koha_api.authenticated() == 1
    assert koha_api.sessionid

  with subtests.test("When deauthentication is done"):
    koha_api.deauthenticate()

  with subtests.test("Then the active session is flushed"):
    assert koha_api.authenticated() == 0
    assert koha_api.sessionid == None

def test_transparent_reauthentication(subtests):
  global borrower

  with subtests.test("Given Lainuri is unauthenticated"):
    assert koha_api.authenticated() == 0

  with subtests.test("When any API request is performed"):
    assert koha_api.get_borrower(borrowernumber=borrower['borrowernumber'])

  with subtests.test("Then a transparent reauthentication occurred"):
    assert koha_api.authenticated() == 1
