import context
import iso15692
import iso15692.compaction
from iso15692 import ByteStream, DataObject


def test_iso25680_decoding_mv():
  iso15692.set_application_defined_compaction_scheme(
    compaction_func=iso15692.compaction.compact_octet_string,
    decompaction_func=iso15692.compaction.decompact_octet_string,
  )

  dob = DataObject(
    tag_memory=bytes(
      b'\x91\x01\x04\x60\x91\xce\x43\x80\x02\x01\xa8\x05\x01\x10\x67\x02'
      b'\x42\x41\x03\x07\x32\x40\xde\x05\xab\x07\x5b\x00\x00\x00\x00\x00'
      b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
      b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
      b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
      b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
      b'\x00\x00\x00\x00'
    ),
  ).decode()

  assert type(dob) == DataObject
  assert dob.get_data_element(1).data == '1620168259'
  assert len(dob.data_elements) == 5
  #assert dob.set_information['numbers_of_parts_in_item'] == 1
  #assert dob.set_information['ordinal_part_number'] == 1
  #assert dob.isil == 'FI-Mamk-M'
  #assert dob.crc == b'\xC4\xCF'

def test_iso25680_decoding_mv_primary_item_identifier():
  iso15692.set_application_defined_compaction_scheme(
    compaction_func=iso15692.compaction.compact_octet_string,
    decompaction_func=iso15692.compaction.decompact_octet_string,
  )

  dob = DataObject(
    tag_memory=bytes(
      b'\x91\x01\x04\x60\x91\xce\x43\x80\x02\x01\xa8\x05\x01\x10\x67\x02'
      b'\x42\x41\x03\x07\x32\x40\xde\x05\xab\x07\x5b\x00\x00\x00\x00\x00'
      b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
      b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
      b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
      b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
      b'\x00\x00\x00\x00'
    ),
  )
  dob.decode_next_data_element() # 1st data element is always the primary item identifier

  assert type(dob) == DataObject
  assert dob.get_data_element(1).data == '1620168259'
  assert len(dob.data_elements) == 1, "Only one data element decoded"

