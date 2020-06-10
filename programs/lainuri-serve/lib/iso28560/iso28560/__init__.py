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

def new_data_object(afi: int, dsfid: int, block_size: int, memory_capacity_blocks: int, tag_memory: bytes = None, object_class: type = None):
  """
  @param object_class, Class of the ISO-standard implementation to choose. Overloads possible bad DSFID-definitions if they are not set correctly.
  """
  if afi > 256:
    raise Exception(f"AFI '{hex(afi)}' is not 1 byte!")
  if not(afi == 0xC2 or afi == 0x07): #C2 == on loan, 07 == on shelf
    log.warning(f"AFI '{hex(afi)}' is not a well-known library value")

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

  def tag_memory(self) -> bytes:
    return self._tag_memory


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

  def encode(self, content_parameter: int, type_of_usage: int, numbers_of_parts_in_item: int, ordinal_part_number: int, primary_item_identifier: str, isil: str):
    if not self._tag_memory: self._tag_memory = bytearray(32)
    self._tag_memory[0] = (content_parameter & 0b00001111) + ((type_of_usage & 0b00001111) << 4)
    self._tag_memory[1] = ordinal_part_number
    self._tag_memory[2] = numbers_of_parts_in_item
    self._encode_primary_item_identifier(primary_item_identifier)
    self._encode_isil(isil)
    self._tag_memory[19:21] = (crc_16_ccitt(self._get_crc_bytes())).to_bytes(2, byteorder='little')
    return self

  def get_basic_block(self):
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
      crc_bytes = self._get_crc_bytes()

    self.crc_check()

  def get_primary_item_identifier(self):
    return self.primary_item_identifier or self._string_from_fixed_field(self._tag_memory[3:19])
  def _encode_primary_item_identifier(self, pii: str):
    byttess = pii.encode('utf-8')
    if len(byttess) > 16: raise ValueError(f"Cannot encode primary item identifier '{pii}'. It is longer than 16 bytes!")
    self._tag_memory[3:3+len(byttess)] = byttess

  def _make_isil(self, byttess):
    isil = self._string_from_fixed_field(byttess)
    return isil[0:2] + '-' + isil[2:]
  def _encode_isil(self, isil: str):
    pass #TODO::
    #byttess = isil.encode('utf-8')
    #if len(byttess) > 16: raise ValueError(f"Cannot encode ISIL '{isil}'. It is longer than 16 bytes!")
    #self._tag_memory[3:3+len(byttess)] = byttess

  def crc_check(self):
    """
    Raises ValueError
    """
    crc_check = crc_16_ccitt(self._get_crc_bytes())
    expected_crc = int.from_bytes(self._tag_memory[19:21], byteorder='little')
    if crc_check != expected_crc:
      raise Exception(f"CRC check mismatch! Expected '{hex(crc_check)}', tag has '{hex(expected_crc)}'")
    return self

  def set_crc(self, byttess: bytes, reverse: bool = False):
    """
    Byteorder of bytes is little-endian, so you might have to reverse the bytes.
    """
    if reverse:
      if hasattr(byttess, 'reverse'): byttess.reverse()
      else:
        byttess = bytearray(byttess)
        byttess.reverse()
    self._tag_memory[19:21] = byttess
    return self

  def _get_crc_bytes(self):
    return bytes([*self._tag_memory[0:19], *self._tag_memory[21:34]])

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
