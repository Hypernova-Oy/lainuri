import iso15692
import iso15692.format

import logging
import yaml

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

  dob_class = object_class if object_class else _get_data_object_class(dsfid=dsfid)
  return dob_class(afi, dsfid, block_size, memory_capacity_blocks, tag_memory)

def _get_data_object_class(dsfid: int):
  dob_class = None

  if dsfid > 256:
    raise Exception(f"DSFID '{hex(dsfid)}' is not 1 byte!")
  if dsfid == 0x06:
    if not dob_class: dob_class = ISO28560_2_Object
  elif dsfid == 0x3E:
    if not dob_class: dob_class = ISO28560_3_Object
  else:
    raise Exception(f"DSFID '{hex(dsfid)}' is not known! Overload your data format class implementation manually.")

  return dob_class



class ISO28560_Object():
  def get_primary_item_identifier(self):
    raise Exception(f"Overload missing from class '{self}'. Overload this for your implementation!")

  def __repr__(self):
    return yaml.dump({'!type': self.__class__, '!id': hex(id(self)), **self.__dict__})



class ISO28560_3_Object(ISO28560_Object):
  """
  Only basic block handling implemented.
  """
  def __init__(self, afi: int, dsfid: int, block_size: int, memory_capacity_blocks: int, tag_memory: bytes = None):
    self._tag_memory = tag_memory
    self.primary_item_identifier = None

  def decode(self, tag_memory: bytes = None):
    self._tag_memory = tag_memory or self._tag_memory
    self.get_basic_block()
    return self

  def get_basic_block(self):
    """
    The basic block contains a number of fixed length data fields. The basic block occupies the first 34 bytes
    (272 bits) on the tag. If the tag has only 32 bytes (256 bits), the layout for the truncated basic block shall be
    used. In this case, no other data can be stored on the tag.
    """
    if len(self._tag_memory) < 32 or len(self._tag_memory) == 33:
      raise Exception(f"tag memory length '{len(self._tag_memory)}' must be 32 or 34 or more. tag_memory='{self._tag_memory}'")
    self.content_parameter = self._tag_memory[0] & 0b00001111
    self.type_of_usage = self._tag_memory[0] & 0b11110000
    self.set_information = {
      'numbers_of_parts_in_item': self._tag_memory[2],
      'ordinal_part_number': self._tag_memory[1],
    }
    self.primary_item_identifier = self.get_primary_item_identifier()
    self.crc = self._tag_memory[19:21]
    if len(self._tag_memory) == 32:
      self.isil = self._make_isil(self._tag_memory[21:32])
      crc_bytes = bytes([*self._tag_memory[0:19], *self._tag_memory[21:32], 0x00, 0x00])
    else:
      self.isil = self._make_isil(self._tag_memory[21:34])
      crc_bytes = bytes([*self._tag_memory[0:19], *self._tag_memory[21:34]])

    crc_check = crc_16_ccitt(crc_bytes)
    if crc_check != int.from_bytes(self.crc, byteorder='little'):
      raise Exception(f"CRC check mismatch! Expected '{hex(crc_check)}', tag has '{self.crc}'")

  def get_primary_item_identifier(self):
    return self.primary_item_identifier or self._string_from_fixed_field(self._tag_memory[3:19])

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



class ISO28560_2_Object(iso15692.DataObject, ISO28560_Object):
  """
  TODO
  """
  def __init__(self, afi: int, dsfid: int, block_size: int, memory_capacity_blocks: int, tag_memory: bytes = None):
    super().__init__(tag_memory=tag_memory)

  def get_primary_item_identifier(self) -> str:
    de = self.get_data_element(1)
    if not de:
      de = self.decode_next_data_element()
    if de.object_identifier != 1:
      raise Exception(f"Data Object is missing primary item identifier!: dob='{self.dob}'")
    return de.data



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
