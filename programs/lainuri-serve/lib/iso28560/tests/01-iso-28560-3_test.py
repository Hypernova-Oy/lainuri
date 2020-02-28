import context

import iso28560

def test_iso28560_3_example_1():
  """
  B.1 Example 1, encoding of truncated basic block
  """
  dob: iso28560.ISO28560_3_Object = iso28560.new_data_object(
      afi=0x07,
      dsfid=0x3E,
      block_size=4,
      memory_capacity_blocks=8,
      tag_memory=bytearray(
        # basic block
        bytes([0b00010001])+  # 2. Content parameter 4 bits 1 5. Type of usage 4 bits 1 (item for circulation)
        b'\x01\x01'  # 4. Set information 2 bytes Item 1 of 1
        b'\x31\x30\x30\x30\x30\x30\x30\x30\x35\x36\x00\x00\x00\x00\x00\x00'  # 1. Primary item identifier  16 bytes  1000000056
        b'\x98\xA4'  # CRC  2 bytes
        b'\x44\x4B\x37\x31\x38\x35\x30\x30\x00\x00\x00\x00\x00'  # 3. Owner institution (ISIL)  13 bytes  DK-718500
      ),
  )
  assert type(dob) == iso28560.ISO28560_3_Object
  assert dob.primary_item_identifier == '1000000056'
  assert dob.set_information['numbers_of_parts_in_item'] == 1
  assert dob.set_information['ordinal_part_number'] == 1
  assert dob.isil == 'DK-718500'
  assert dob.crc == b'\x98\xA4'

def test_iso28560_3_example_2():
  """
  B.2 Example 2, encoding of basic block and structured extension blocks
  """
  dob: iso28560.ISO28560_3_Object = iso28560.new_data_object(
      afi=0x07,
      dsfid=0x3E,
      block_size=3,
      memory_capacity_blocks=27,
      tag_memory=bytearray(
        # basic block
        bytes([0b00010001])+  # 1     1 (item for circulation)
        b'\x01\x01'           # Item 1 of 1
        b'\x31\x30\x30\x30\x30\x30\x30\x31\x33\x36\x00\x00\x00\x00\x00\x00' # primary identifier '1000000136'
        b'\x36\x15' # CRC
        b'\x44\x4B\x37\x31\x38\x35\x30\x30\x00\x00\x00\x00\x00' # ISIL 'DK-718500'
        # library extension block
        b'\x05' # length 5 bytes
        b'\x01\x00' # data block ID           1 (library ext. block)
        b'\x05' # XOR checksum
        b'\x01' # 19. Media format (other)        1 (book)
        # acquisition extension block
        b'\x22' # Length 34 bytes
        b'\x02\x00' # Data block ID     2 (acquisition ext. block)
        b'\x71' # XOR checksum
        b'\x42\x6F\x67\x76\x6F\x67\x6E\x65\x6E\x00' # 9. Supplier identifier         Bogvognen
        b'\x31\x32\x33\x34\x35\x36\x37\x38\x39\x30\x00' # 18. Product identifier local      1234567890
        b'\x00' # 10. Order number         Empty
        b'\x61\x37\x38\x39\x36\x35\x36\x63\x00' # 21. Supplier invoice number      a789656c
      ),
  )
  assert type(dob) == iso28560.ISO28560_3_Object
  assert dob.primary_item_identifier == '1000000136'
  assert dob.set_information['numbers_of_parts_in_item'] == 1
  assert dob.set_information['ordinal_part_number'] == 1
  assert dob.isil == 'DK-718500'
  assert dob.crc == b'\x36\x15'

def test_iso28560_3_mv():
  dob: iso28560.ISO28560_3_Object = iso28560.new_data_object(
      afi=0x07,
      dsfid=0x3E,
      block_size=3,
      memory_capacity_blocks=27,
      tag_memory=bytearray(b'\x11\x01\x011620154429\x00\x00\x00'
                           b'\x00\x00\x00\xc4\xcfFIMamk-M\x00\x00\x00'
                           b'\x00\x00\x06e\x00vta\x00\x00\x00\x00'
                           b'\x00\x00\x00\x00\x00\x00\x00\x00'
                           b'\x00\x00\x00\x00\x00\x00\x00\x00'
                           b'\x00\x00\x00\x00\x00\x00\x00\x00'
                           b'\x00\x00\x00\x00\x00\x00\x00\x00'
                           b'\x00\x00\x00\x00\x00\x00\x00\x00'),
  )
  assert type(dob) == iso28560.ISO28560_3_Object
  assert dob.primary_item_identifier == '1620154429'
  assert dob.set_information['numbers_of_parts_in_item'] == 1
  assert dob.set_information['ordinal_part_number'] == 1
  assert dob.isil == 'FI-Mamk-M'
  assert dob.crc == b'\xC4\xCF'