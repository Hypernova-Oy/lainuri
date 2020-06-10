import context
import iso28560

def test_crc_16_ccitt():
  assert iso28560.crc_16_ccitt(b'RFID tag data model') == 0x1AEE

def test_crc_16_ISO28560_3_lengths():
  dob = iso28560.ISO28560_3_Object(afi=0x00, dsfid=0x00, block_size=3, memory_capacity_blocks=16, tag_memory=bytearray(32))
  dob.set_crc(bytes([0x45, 0x2A]))
  assert dob.crc_check()
  assert dob.tag_memory() == bytes(19) + bytes([0x45, 0x2A]) + bytes(11)

  dob = iso28560.ISO28560_3_Object(afi=0x00, dsfid=0x00, block_size=3, memory_capacity_blocks=16, tag_memory=bytearray(34))
  dob.set_crc(bytes([0xF1, 0x4C]), reverse=True)
  assert dob.crc_check()
  assert dob.tag_memory() == bytes(19) + bytes([0x4C, 0xF1]) + bytes(13)
