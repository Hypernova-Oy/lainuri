import context
import iso15692.compaction

def test_iso15692_encode_compacted_object_length():
  asserts = [
    [bytes(1),      b'\x01'],
    [bytes(12),     b'\x0C'],
    [bytes(127),    b'\x7f'],
    [bytes(128),    b'\x81\x00'],
    [bytes(129),    b'\x81\x01'],
    [bytes(138),    b'\x81\x0A'],
    [bytes(16383),  b'\xff\x7f'],
    [bytes(16384),  b'\x81\x80\x00'],
  ]
  for a in asserts:
    assert iso15692.compaction.encode_compacted_object_length(a[0]) == a[1]
