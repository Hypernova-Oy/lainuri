import context
import iso28560

def test_crc_16_ccitt():
  assert iso28560.crc_16_ccitt(b'RFID tag data model') == 0x1AEE
