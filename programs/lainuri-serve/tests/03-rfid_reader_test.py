#!/usr/bin/python3

import context

import lainuri.config
from lainuri.constants import Status
import lainuri.event
import lainuri.event_queue
import lainuri.exception.rfid as exception_rfid
import lainuri.koha_api
import lainuri.rfid_reader
from lainuri.RL866.tag import Tag

import iso28560
import time
import unittest.mock

rfid_reader = None

def test_rfid_reader_system_information(subtests):
  global rfid_reader

  with subtests.test("Given a rfid reader"):
    rfid_reader = lainuri.rfid_reader.get_rfid_reader() if not rfid_reader else rfid_reader
    assert rfid_reader

  with subtests.test("And a Koha API authentication"):
    assert lainuri.koha_api.koha_api.authenticate()

  with subtests.test("When rfid tags are inventoried"):
    rfid_reader.do_inventory()

  with subtests.test("Then rfid tags are present"):
    assert len(rfid_reader.tags_present) > 0

  with subtests.test("And rfid tag is fleshed out with system information and tag memory details"):
    tag = rfid_reader.tags_present[0]
    assert tag.afi() != None
    assert tag.dsfid() != None
    assert tag.block_size() != None
    assert tag.memory_capacity_blocks() != None
    assert tag.iso25680_get_primary_item_identifier() != None

  with subtests.test("And new rfid-tags are discovered"):
    event_rfid_tags_new = lainuri.event_queue.history[0]
    assert type(event_rfid_tags_new) == lainuri.event.LERFIDTagsNew
    assert len(event_rfid_tags_new.tags_new) > 0
    assert event_rfid_tags_new.tags_new[0]['item_barcode']
    assert len(event_rfid_tags_new.tags_present) > 0
    assert event_rfid_tags_new.tags_present[0]['item_barcode']

def test_rfid_reader_exception_handling_finally_disconnect_tag():
  tag = rfid_reader.tags_present[0]
  tag.connect(b'\x00') #Mock a connection
  #import pdb; pdb.set_trace() # To debug this failing test a debugger is needed because the finally-handler by design hides all exceptions
  tag_resp = lainuri.rfid_reader._finally_tag_disconnect(rfid_reader, tag)
  assert tag == tag_resp

def test_rfid_tag_data_format_overload(subtests):
  tag = None

  with subtests.test("Set up: Data format overloading rules"):
    assert lainuri.config.write_config('devices.rfid-reader.iso28560-data-format-overloads', [
      {'dsfid':  0, #'0x00',
       '!class': 'ISO28560_3_Object'},
      {'afi':  194, #'0xC2',
       '!class': 'ISO28560_3_Object'},
    ]) == {
      'old_value': [
        {'dsfid':  0,
         '!class': 'ISO28560_3_Object'}
      ],
      'new_value': [
        {'dsfid':  0,
        '!class': 'ISO28560_3_Object'},
        {'afi':  194,
        '!class': 'ISO28560_3_Object'},
      ],
      'variable': 'devices.rfid-reader.iso28560-data-format-overloads',
    }

  with subtests.test("Scenario: Data format correctly detected for ISO28560_2_Object"):

    with subtests.test("(ISO28560_2_Object) Given a rfid tag"):
      tag = Tag('12341234')
      tag.dsfid(0x06)
      tag.afi(0x00)
      assert tag

    with subtests.test("(ISO28560_2_Object) Then the rfid tag is checked for data format implementation"):
      assert tag.get_data_object_format_implementation() == iso28560.ISO28560_2_Object

  with subtests.test("Scenario: Data format correctly detected for ISO28560_3_Object"):

    with subtests.test("(ISO28560_3_Object) Given a rfid tag"):
      tag = Tag('12341234')
      tag.dsfid(0x3E)
      tag.afi(0xC2)
      assert tag

    with subtests.test("(ISO28560_3_Object) Then the rfid tag is checked for data format implementation"):
      assert tag.get_data_object_format_implementation() == iso28560.ISO28560_3_Object

  with subtests.test("Scenario: Data format overloaded based on DSFID"):

    with subtests.test("(DSFID) Given a rfid tag"):
      tag = Tag('12341234')
      tag.dsfid(0x00)
      tag.afi(0xC2)
      assert tag

    with subtests.test("(DSFID) Then the rfid tag is checked for data format implementation"):
      assert tag.get_data_object_format_implementation() == iso28560.ISO28560_3_Object

  with subtests.test("Scenario: Data format overloaded based on AFI"):

    with subtests.test("(AFI) Given a rfid tag"):
      tag = Tag('12341234')
      tag.dsfid(0x00)
      tag.afi(0x07)
      assert tag

    with subtests.test("(AFI) Then the rfid tag is checked for data format implementation"):
      assert tag.get_data_object_format_implementation() == iso28560.ISO28560_3_Object

def test_rfid_reader_inventory_polling_thread(subtests):
  global rfid_reader

  with subtests.test("Given a rfid reader"):
    rfid_reader = lainuri.rfid_reader.get_rfid_reader() if not rfid_reader else rfid_reader
    assert rfid_reader

  with subtests.test("When the rfid reader start polling for inventory"):
    rfid_reader.start_polling_rfid_tags()
    assert context.poll_thread_is_alive(True, rfid_reader.daemon)
    time.sleep(1) # Give time to do the inventory

  with subtests.test("Then the rfid tags are automatically inventoried"):
    assert len(lainuri.rfid_reader.get_current_inventory_status()) > 0

  with subtests.test("Finally the polling thread is terminated"):
    rfid_reader.stop_polling_rfid_tags()
    assert context.poll_thread_is_alive(False, rfid_reader.daemon)



def mock_flesh_tag_details1(tag):
  raise exception_rfid.TagMalformed(id="tag serial number", description="nice error description")
def mock_flesh_tag_details2(tag):
  raise exception_rfid.RFIDCommand(id="tag serial number", description="nice command description")

def test_rfid_reader_inventory_polling_exception_handling__individual_tag_malformed(subtests):
  global rfid_reader
  assert lainuri.event_queue.flush_all()

  with unittest.mock.patch.object(lainuri.rfid_reader.RFID_Reader, 'flesh_tag_details', side_effect=mock_flesh_tag_details1) as raise_on_tag_fleshing:
    with subtests.test("Given an RFID Reader which is rigged to fail when fleshing tag details"):
      rfid_reader = lainuri.rfid_reader.get_rfid_reader() if not rfid_reader else rfid_reader
      rfid_reader.tags_present = []

    with subtests.test("When polling for inventory, an exception is thrown"):
      rfid_reader.rfid_poll_daemon()

    with subtests.test("And a LEServerStatusResponse is generated due to a RFID reader exception"):
      event = lainuri.event_queue.pop_event(1)
      assert type(event) == lainuri.event.LEServerStatusResponse
      assert event.statuses['rfid_reader_status'] == Status.ERROR

    with subtests.test("Then a TagMalformed-exception is caught during polling and scheduled to the GUI"):
      event = lainuri.event_queue.pop_event(1)
      assert type(event) == lainuri.event.LERFIDTagsNew
      assert event.states['exception']['type'] == 'TagMalformed'
      assert event.states['exception']['err_repeated'] == 1
      assert event.tags_new == []
      assert event.tags_present == []
      assert event.status == Status.ERROR

def test_rfid_reader_inventory_polling_exception_handling__more_generic_rfid_error(subtests):
  global rfid_reader
  assert lainuri.event_queue.flush_all()

  with unittest.mock.patch.object(lainuri.rfid_reader.RFID_Reader, 'flesh_tag_details', side_effect=mock_flesh_tag_details2) as raise_on_tag_fleshing:
    with subtests.test("Given an RFID Reader which is rigged to fail when fleshing tag details"):
      rfid_reader = lainuri.rfid_reader.get_rfid_reader() if not rfid_reader else rfid_reader
      rfid_reader.tags_present = []

    with subtests.test("When polling for inventory, an exception is thrown"):
      rfid_reader.rfid_poll_daemon()

    with subtests.test("Then a RFID-exception is caught during polling and scheduled to the GUI"):
      event = lainuri.event_queue.pop_event(1)
      assert type(event) == lainuri.event.LERFIDTagsNew
      assert event.states['exception']['type'] == 'RFID'
      assert event.states['exception']['err_repeated'] == 2
      assert event.tags_new == []
      assert event.tags_present == []
      assert event.status == Status.ERROR

    #with subtests.test("And a LEServerStatusResponse is NOT generated due to a RFID reader being in ERROR-state"):
    #  context.assert_raises('Lainuri event_queue is empty', lainuri.event_queue.queue.Empty, '', lambda: lainuri.event_queue.pop_event(1))

def test_rfid_reader_inventory_polling_exception_handling__rfid_reader_reset_after_too_many_errors(subtests):
  global rfid_reader
  assert lainuri.event_queue.flush_all()

  with unittest.mock.patch.object(lainuri.rfid_reader.RFID_Reader, 'flesh_tag_details', side_effect=mock_flesh_tag_details2) as raise_on_tag_fleshing:
    with subtests.test("Given an RFID Reader which is rigged to fail when fleshing tag details"):
      rfid_reader = lainuri.rfid_reader.get_rfid_reader() if not rfid_reader else rfid_reader
      rfid_reader.tags_present = []

    with subtests.test("When polling for inventory, an exception is thrown"):
      rfid_reader.rfid_poll_daemon()

    with subtests.test("Then a RFID-exception is caught during polling and scheduled to the GUI"):
      event = lainuri.event_queue.pop_event(1)
      assert type(event) == lainuri.event.LERFIDTagsNew
      assert event.states['exception']['type'] == 'RFIDReset'
      assert event.states['exception']['err_repeated'] == 3
      assert event.tags_new == []
      assert event.tags_present == []
      assert event.status == Status.ERROR

    #with subtests.test("And a LEServerStatusResponse is NOT generated due to a RFID reader being in ERROR-state"):
    #  context.assert_raises('Lainuri event_queue is empty', lainuri.event_queue.queue.Empty, '', lambda: lainuri.event_queue.pop_event(1))
