import iso15692
import iso15692.format
import iso15692.util

import logging

log = logging.getLogger(__name__)

data_element_types = {
  1: {
    'name': 'Primary item identifier',
    'status': 'Mandatory',
    'format': iso15692.format.IRV,
    'lock': 'should',
  },
  '2': {
    'name': 'Content parameter',
    'status': 'Optional',
    'format': 'Bit mapped code (see 6.3)',
    'lock': 'optional',
  },
  '3': {
    'name': 'Owner institution (ISIL)',
    'status': 'Optional',
    'format': 'Variable length field (maximum of 16 characters)',
    'lock': 'optional',
  },
}

def new_data_object(afi: int, dsfid: int, block_size: int, memory_capacity_blocks: int, tag_memory: bytes, object_class: type = None):
  """
  @param object_class, Class of the ISO-standard implementation to choose. Overloads possible bad DSFID-definitions if they are not set correctly.
  """
  if afi > 256:
    raise Exception(f"AFI '{hex(afi)}' is not 1 byte!")
  if not(afi == 0xC2 or afi == 0x07): #C2 == on loan, 07 == on shelf
    log.warn(f"AFI '{hex(afi)}' is not a well-known library value")

  if dsfid > 256:
    raise Exception(f"DSFID '{hex(dsfid)}' is not 1 byte!")
  access_method = dsfid >> 3
  if access_method == 0b000:
    if not object_class: object_class = ISO28560_2_Object
  elif access_method == 0b111:
    if not object_class: object_class = ISO28560_3_Object
  else:
    raise Exception(f"access method '{bin(access_method)}' is not known!")

  data_format = dsfid & 0b00011111
  if object_class == ISO28560_2_Object and data_format != 0b00110:
    log.warn(f"data format '{bin(data_format)}' is not a well-known library value")
  elif object_class == ISO28560_3_Object and data_format != 0b11110:
    log.warn(f"data format '{bin(data_format)}' is not a well-known library value")

  return object_class(afi, dsfid, block_size, memory_capacity_blocks, tag_memory)



class ISO28560_3_Object():
  """
  Only basic block handling implemented.
  """
  def __init__(self, afi: int, dsfid: int, block_size: int, memory_capacity_blocks: int, tag_memory: bytes):
    self.get_basic_block(tag_memory)

  def get_basic_block(self, tag_memory: bytes):
    """
    The basic block contains a number of fixed length data fields. The basic block occupies the first 34 bytes
    (272 bits) on the tag. If the tag has only 32 bytes (256 bits), the layout for the truncated basic block shall be
    used. In this case, no other data can be stored on the tag.
    """
    if len(tag_memory) < 32 or len(tag_memory) == 33:
      raise Exception(f"tag memory length '{len(tag_memory)}' must be 32 or 34 or more. tag_memory='{tag_memory}'")
    self.content_parameter = tag_memory[0] & 0b00001111
    self.type_of_usage = tag_memory[0] & 0b11110000
    self.set_information = {
      'numbers_of_parts_in_item': tag_memory[2],
      'ordinal_part_number': tag_memory[1],
    }
    self.primary_item_identifier = self._string_from_fixed_field(tag_memory[3:19])
    self.crc = tag_memory[19:21]
    if len(tag_memory) == 32:
      self.isil = self._make_isil(tag_memory[21:32])
      crc_bytes = bytes([*tag_memory[0:19], *tag_memory[21:32], 0x00, 0x00])
    else:
      self.isil = self._make_isil(tag_memory[21:34])
      crc_bytes = bytes([*tag_memory[0:19], *tag_memory[21:34]])

    crc_check = crc_16_ccitt(crc_bytes)
    if crc_check != int.from_bytes(self.crc, byteorder='little'):
      raise Exception(f"CRC check mismatch! Expected '{hex(crc_check)}', tag has '{self.crc}'")

  def _make_isil(self, byttess):
    isil = self._string_from_fixed_field(byttess)
    return isil[0:2] + '-' + isil[2:]

  def _string_from_fixed_field(self, byttess):
    """
    ISO 28560-3 encodes string as UTF-8
    """
    i = 0
    for b in byttess:
      if byttess[i] == 0x00:
        break
      i = i+1
    return byttess[0:i].decode('utf8')



class ISO28560_2_Object():
  """
  TODO
  """
  def __init__(self, afi: int, dsfid: int, block_size: int, memory_capacity_blocks: int, tag_memory: bytes):
    # Set the tag memory and iterator to browse it
    self.data_elements = {}
    self.dob = iso15692.get_data_object(iso15692.util.ByteStream(tag_memory))

  def get_primary_item_identifier(self) -> str:
    return self.dob.get_data_element(1).data



def crc_16_ccitt(bytess):
  crc_poly = 0x1021
  crc_sum = 0xFFFF
  for c in bytess:
    i = 0
    xor_flag = False
    c <<= 8
    for _ in range(0,8):
      xor_flag = ((crc_sum ^ c) & 0x8000) != 0
      crc_sum = crc_sum << 1
      if (xor_flag):
        crc_sum = crc_sum ^ crc_poly
      c = c << 1
    crc_sum &= 0xffff

  return crc_sum
