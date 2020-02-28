import context
import iso15692
import iso15692.compaction
from iso15692.util import ByteStream

def test_iso15690_example_annex_p():
  dob = iso15692.get_data_object(
    tag_memory=ByteStream(bytes(
      b'\x91\x05\x08\x00\x2B\xDC\x54\x5E\x14\xD6\x4E\x80\x80\x80\x80\x80'
      b'\xC7\x00\x05\x04\x2C\x72\x61\x98'
      b'\x19\x04\x01\x32\x91\x5F'
      b'\x7F\x02\x02\x54\x1C'
      b'\x6E\x03\xA2\xB3\x80'
    ))
  )
  assert dob.get_data_element(1).data  == '0123456789121345678'
  assert dob.get_data_element(7).data  == 'AB12XY'
  assert dob.get_data_element(9).data  == '20091231'
  assert dob.get_data_element(17).data == 'JPN'
  assert dob.get_data_element(14).data == 'A2B380'
