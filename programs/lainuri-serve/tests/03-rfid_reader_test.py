#!/usr/bin/python3

import context

import lainuri.config
import lainuri.websocket_server
from lainuri.rfid_reader import RFID_Reader
from lainuri.RL866.tag import Tag

import iso28560

rfid_reader = None

def test_rfid_reader(subtests):
  rfid_reader = None

  with subtests.test("Given a rfid reader"):
    rfid_reader = RFID_Reader()
    assert rfid_reader

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
      tag.afi(0xC2)
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

