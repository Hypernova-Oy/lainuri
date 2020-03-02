import context

import iso15692
import iso15692.compaction
import iso28560

def test_iso28560_2_mv():

  iso15692.set_application_defined_compaction_scheme(
    compaction_func=iso15692.compaction.compact_octet_string,
    decompaction_func=iso15692.compaction.decompact_octet_string,
  )

  dob: iso28560.ISO28560_2_Object = iso28560.new_data_object(
      afi=0x07,
      dsfid=0x06,
      block_size=3,
      memory_capacity_blocks=27,
      tag_memory=bytearray(
                    b'\x91\x01\x04\x60\x91\xce\x43\x80\x02\x01\xa8\x05\x01\x10\x67\x02'
                    b'\x42\x41\x03\x07\x32\x40\xde\x05\xab\x07\x5b\x00\x00\x00\x00\x00'
                    b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
                    b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
                    b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
                    b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
                    b'\x00\x00\x00\x00'),
  ).decode()
  assert type(dob) == iso28560.ISO28560_2_Object
  assert dob.get_primary_item_identifier() == '1620168259'


def test_iso28560_2_mv_get_primary_item_identifier():

  dob: iso28560.ISO28560_2_Object = iso28560.new_data_object(
      afi=0x07,
      dsfid=0x06,
      block_size=3,
      memory_capacity_blocks=27,
      tag_memory=bytearray(
                    b'\x91\x01\x04\x60\x91\xce\x43\x80\x02\x01\xa8\x05\x01\x10\x67\x02'
                    b'\x42\x41\x03\x07\x32\x40\xde\x05\xab\x07\x5b\x00\x00\x00\x00\x00'
                    b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
                    b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
                    b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
                    b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
                    b'\x00\x00\x00\x00'),
  )
  assert type(dob) == iso28560.ISO28560_2_Object
  assert dob.get_primary_item_identifier() == '1620168259'
