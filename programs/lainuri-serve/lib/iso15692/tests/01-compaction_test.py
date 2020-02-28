import context
import iso15692.compaction

def test_iso15692_compaction_integer():
  assert iso15692.compaction.get_compaction_scheme(0b001)('123456789012') == b'\x1C\xBE\x99\x1A\x14'

def test_iso15692_decompaction_integer():
  assert iso15692.compaction.get_decompaction_scheme(0b001)(b'\x1C\xBE\x99\x1A\x14') == '123456789012'

def test_iso15692_compaction_numeric():
  assert iso15692.compaction.get_compaction_scheme(0b010)('410') == bytes([0b01000001, 0b00001111])

def test_iso15692_decompaction_numeric():
  assert iso15692.compaction.get_decompaction_scheme(0b010)(bytes([0b01000001, 0b00001111])) == '410'

def test_iso15692_compaction_5_bit():
  assert iso15692.compaction.get_compaction_scheme(0b011)('JPN') ==  b'\x54\x1C'

def test_iso15692_decompaction_5_bit():
  assert iso15692.compaction.get_decompaction_scheme(0b011)(b'\x54\x1C') == 'JPN'

def test_iso15692_compaction_6_bit():
  assert iso15692.compaction.get_compaction_scheme(0b100)('ABC123456') ==  b'\x04\x20\xF1\xCB\x3D\x35\xDA'

def test_iso15692_decompaction_6_bit():
  assert iso15692.compaction.get_decompaction_scheme(0b100)(b'\x04\x20\xF1\xCB\x3D\x35\xDA') == 'ABC123456'
