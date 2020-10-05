#!/usr/bin/python3

import context
from lainuri.config import get_config

import lainuri.koha_api
from lainuri.constants import SortBin, Status
import lainuri.sorting

def mock_handle_html(mock_html_path, barcode):
  return lainuri.koha_api.koha_api._checkin_check_statuses(barcode, context.soapify_mock_response(mock_html_path))
def mock_handle_html_checkout(mock_html_path, barcode):
  soup = context.soapify_mock_response(mock_html_path)
  return lainuri.koha_api.koha_api._checkout_check_statuses(barcode, soup, *lainuri.koha_api.koha_api._parse_html(soup))

def test_sorting_checkin_error_no_item_01():
  (status, states) = mock_handle_html('koha_api_20_06/checkin_error_no_item_01.html', 'missing-barcode')

  assert states == {'no_item': True}
  assert status == Status.ERROR
  assert lainuri.sorting.sort(status, states) == SortBin.REJECT

def test_sorting_checkin_success_01():
  (status, states) = mock_handle_html('koha_api_20_06/checkin_success_01.html', '1233')

  assert status == Status.SUCCESS
  assert len(states) == 0
  assert lainuri.sorting.sort(status, states) == SortBin.OK

def test_sortin_checking_success_hold_waiting_01():
  (status, states) = mock_handle_html('koha_api_20_06/checkin_with_hold_waiting_01.html', '1620128264')

  assert states == {'hold_found': '139058'}
  assert status == Status.SUCCESS
  assert lainuri.sorting.sort(status, states) == SortBin.ERROR

def test_sorting_checkin_success_hold_01():
  (status, states) = mock_handle_html('koha_api_20_06/checkin_with_hold_01.html', '1620111663')

  assert states == {'hold_found': '132953'}
  assert status == Status.SUCCESS
  assert lainuri.sorting.sort(status, states) == SortBin.ERROR

def test_sorting_checkin_success_hold_not_checked_out_01():
  (status, states) = mock_handle_html('koha_api_20_06/checkin_with_hold_not_checked_out_01.html', 'kis12345')

  assert states == {'hold_found': '33', 'not_checked_out': True}
  assert status == Status.SUCCESS
  assert lainuri.sorting.sort(status, states) == SortBin.ERROR

def test_sorting_checkin_success_transfer_01():
  (status, states) = mock_handle_html('koha_api_20_06/checkin_with_transfer_01.html', 'ki12345')

  assert states == {'return_to_another_branch': 'HAMKin kirjasto'}
  assert status == Status.SUCCESS
  assert lainuri.sorting.sort(status, states) == SortBin.ERROR

def test_sorting_checkin_success_transfer_02():
  (status, states) = mock_handle_html('koha_api_20_06/checkin_with_transfer_02.html', '1623207211')

  assert states == {'return_to_another_branch': 'Kouvolan kampuskirjasto', 'not_checked_out': True}
  assert status == Status.SUCCESS
  assert lainuri.sorting.sort(status, states) == SortBin.ERROR

def test_sorting_checkout_success_01():
  (status, states) = mock_handle_html('koha_api_20_06/checkin_with_hold_not_checked_out_01.html', 'kis12345')

  assert states == {'hold_found': '33', 'not_checked_out': True}
  assert status == Status.SUCCESS
  assert lainuri.sorting.sort(status, states) == SortBin.ERROR

def test_parsing_checkout_success_01():
  (status, states) = mock_handle_html_checkout('koha_api_20_06/checkout_success_01.html', 'ki12345')

  assert states == {}
  assert status == Status.SUCCESS

def test_parsing_checkout_impossible_01():
  (status, states) = mock_handle_html_checkout('koha_api_20_06/checkout_impossible_01.html', 'impossible?!')

  assert states == {'checkout_impossible': True}
  assert status == Status.ERROR
