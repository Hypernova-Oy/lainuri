import context
import iso15692
from iso15692.util import ByteStream

def test_iso15690_example_annex_p():
  bs = ByteStream(b'\x7F\x02')
  import pdb; pdb.set_trace()
  assert iso15692.get_precursor(bs) == {
    'offset': 0,
    'compaction_type_code': 0b011,
    'object_identifier': 17,
  }
