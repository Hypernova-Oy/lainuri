import context
import iso15692
from iso15692 import DataObject

def test_iso15690_example_annex_p():
  bs = b'\x7F\x02'
  dob = DataObject(bs)
  assert dob.get_precursor() == {
    'offset': 0,
    'compaction_type_code': 0b111,
    'object_identifier': 17,
  }
