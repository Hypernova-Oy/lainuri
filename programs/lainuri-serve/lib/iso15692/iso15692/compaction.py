from bitarray import bitarray, frozenbitarray
import logging
import re

from iso15692.util import ByteStream

endian='little'
default_encoding='iso-8859-1'
bin00  = frozenbitarray(initial='00',  endian='big')
bin01  = frozenbitarray(initial='01',  endian='big')
bin010 = frozenbitarray(initial='010', endian='big')

"""
Overload this from your program to define you application specific compaction scheme.

  iso15692.set_application_defined_compaction_scheme()

You can change it as any time and the existing references to application defined compaction scheme implementation are updated too.
"""
application_defined_compaction_scheme = [
  lambda args: (_ for _ in ()).throw(ValueError("Compaction scheme 'Application defined' is not defined!")),
  lambda args: (_ for _ in ()).throw(ValueError("Decompaction scheme 'Application defined' is not defined!")),
]

def get_compaction_scheme_from_precursor(precursor_byte: int):
  return get_compaction_scheme((precursor_byte & 0b01110000) >> 4)
def get_compaction_scheme(compaction_type_code: int):
  return iso_15962_compaction_schemes.get(compaction_type_code, None)[0]

def get_decompaction_scheme_from_precursor(precursor_byte: int):
  return get_decompaction_scheme((precursor_byte & 0b01110000) >> 4)
def get_decompaction_scheme(compaction_type_code: int):
  return iso_15962_compaction_schemes.get(compaction_type_code, None)[1]


def detect_best_compaction_scheme(data: str) -> callable:
  try:
    if validate_compaction_integer(data): return compact_integer
  except ValueError:
    pass
  try:
    if validate_compaction_numeric(data): return compact_numeric
  except ValueError:
    pass

#41 to 5F  Length of object > 2 bytes  5 bit code
#20 to 5F  Length of object > 3 bytes  6 bit code
#00 to 7E  Length of object > 7 bytes  7 bit code
#00 to FF  N/A  octet string


def encode_compacted_object_length(byttes: bytes) -> bytes:
  bit_len_bytes = len(byttes).bit_length()
  if bit_len_bytes <= 7:  #if len(byttes) < 128:
    return bytes([len(byttes)])
  elif bit_len_bytes <= 14:  #elif len(byttes) < 16384:
    return bytes([
      (len(byttes) & 0b11111110000000) >> 7 | 128,
      (len(byttes) & 0b00000001111111)
    ])
  elif bit_len_bytes <= 21:  #elif len(byttes) < 2097151:
    return bytes([
      (len(byttes) & 0b111111100000000000000) >> 14 | 128,
      (len(byttes) & 0b000000011111110000000) >> 7 | 128,
      (len(byttes) & 0b000000000000001111111)
    ])

def decode_compacted_object_length(tag_memory: ByteStream) -> int:
  first_byte = tag_memory.next()
  if(first_byte & 0b10000000):
    length_bytes = bytearray([first_byte])
    while(tag_memory.peek() & 0b10000000):
      length_bytes.append(tag_memory.next())
    length_bytes.append(tag_memory.next())
    return int.from_bytes(length_bytes, byteorder='big')
  return first_byte

def compact_application_defined(data: str) -> bytes:
  """
  Lazily invoke the application-defined compaction, so it can be set or changed between invocations.
  """
  global application_defined_compaction_scheme
  return application_defined_compaction_scheme[0](data)

def decompact_application_defined(data: bytes) -> str:
  """
  Lazily invoke the application-defined decompaction, so it can be set or changed between invocations.
  """
  global application_defined_compaction_scheme
  return application_defined_compaction_scheme[1](data)

def compact_integer(integer: str) -> bytes:
  validate_compaction_integer(integer)
  integer = int(integer)
  return integer.to_bytes((integer.bit_length() + 7) // 8, byteorder='big')

def decompact_integer(byttes: bytes) -> str:
  return validate_compaction_integer(str(int.from_bytes(byttes, byteorder='big')))

validate_compaction_integer_regex = re.compile('^[1-9]+[0-9]+$')
def validate_compaction_integer(integer: str) -> str:
  if len(integer) > 19:
    raise ValueError(f"Integer '{integer}' is longer than 19 bytes")
  if len(integer) < 2:
    raise ValueError(f"Integer '{integer}' is too short. Minimum length 2 bytes.")
  if not validate_compaction_integer_regex.search(integer):
    raise ValueError(f"Integer '{integer}' is not numbers as a string. Not starting with 0.")
  return integer

def compact_numeric(numeric: str) -> bytes:
  validate_compaction_numeric(numeric)
  bits = bitarray(endian='big')
  for c in numeric:
    bin_4_bit = f'{int(c):b}' #big endian bit string
    #bin_4_bit = bin_4_bit[::-1]
    if len(bin_4_bit) < 4:
      bin_4_bit = '0' * (4 - len(bin_4_bit)) + bin_4_bit
    else:
      bin_4_bit = bin_4_bit[-4:]
    bits.extend(bin_4_bit)

  partial_byte_bits = bits.length() % 8
  if partial_byte_bits != 0:
    bits.extend('1111')

  return bits.tobytes()

def decompact_numeric(byttes: bytes) -> str:
  numeric = []
  for b in byttes:
    numeric.append(str(b >> 4))
    second_number = b & 0b00001111
    if second_number > 9:
      next
    else:
      numeric.append(str(second_number))
  return validate_compaction_numeric(''.join(numeric))

validate_compaction_numeric_regex = re.compile('^[0-9]+$')
def validate_compaction_numeric(numeric: str):
  if len(numeric) < 2:
    raise ValueError(f"Numeric '{numeric}' is too short. Minimum length 2 bytes.")
  if not validate_compaction_numeric_regex.search(numeric):
    raise ValueError(f"Numeric hex='{numeric.encode(default_encoding).hex()}' is not numbers as a string.")
  return numeric

def compact_5_bit(string: str) -> bytes:
  validate_compaction_5_bit(string)
  bits = bitarray(endian='big')

  for byte in string.encode(default_encoding):
    bin_5_bit = f'{byte:b}'
    if len(bin_5_bit) < 5:
      bin_5_bit = '0' * (5 - len(bin_5_bit)) + bin_5_bit
    else:
      bin_5_bit = bin_5_bit[-5:]
    bits.extend(bin_5_bit)

  partial_byte_bits = bits.length() % 8
  if partial_byte_bits != 0:
    bits.extend('0' * (8-partial_byte_bits))

  return bits.tobytes()

def decompact_5_bit(byttes: bytes) -> str:
  bits = bitarray(endian='big')
  bits.frombytes(byttes)
  byttes = b''

  for i in range(5,bits.length(), 5):
    byttes = byttes + (bin010 + bits[i-5:i]).tobytes()

  if byttes[-1] == 0x40:
    byttes = byttes[:-1]

  return validate_compaction_5_bit(byttes.decode(default_encoding))

validate_compaction_5_bit_regex = re.compile('^[\x41-\x5F]{3,}$')
def validate_compaction_5_bit(string: str):
  if not validate_compaction_6_bit_regex.search(string):
    raise ValueError(f"String '{string}' hex='{string.encode(default_encoding).hex()}' cannot be 5_bit compacted.")
  return string

def compact_6_bit(string: str) -> bytes:
  validate_compaction_6_bit(string)
  bits = bitarray(endian='big')

  for byte in string.encode(default_encoding):
    bin_6_bit = f'{byte:b}'
    if len(bin_6_bit) < 6:
      bin_6_bit = '0' * (6 - len(bin_6_bit)) + bin_6_bit
    else:
      bin_6_bit = bin_6_bit[-6:]
    bits.extend(bin_6_bit)

  partial_byte_bits = bits.length() % 8
  if partial_byte_bits != 0:
    bits.extend('1' + '0' * (8-partial_byte_bits-1))

  return bits.tobytes()

def decompact_6_bit(byttes: bytes) -> str:
  bits = bitarray(endian='big')
  bits.frombytes(byttes)
  byttes = b''

  for i in range(6,bits.length(), 6):
    bin_6_bit = bits[i-6:i]
    if bin_6_bit[0] == True:
      byttes = byttes + (bin00 + bin_6_bit).tobytes()
    else:
      byttes = byttes + (bin01 + bin_6_bit).tobytes()

  return validate_compaction_6_bit(byttes.decode(default_encoding))

validate_compaction_6_bit_regex = re.compile('^[\x20-\x5F]+[^\x20]$')
def validate_compaction_6_bit(string: str):
  if len(string) < 4:
    raise ValueError(f"String '{string}' is too short. Minimum length 4 bytes.")
  if not validate_compaction_6_bit_regex.search(string):
    raise ValueError(f"String '{string}' hex='{string.encode(default_encoding).hex()}' cannot be 6_bit compacted.")
  return string

def compact_octet_string(octets: str) -> bytes:
  return octets.encode(default_encoding)

def decompact_octet_string(octets: bytes) -> str:
  return octets.decode(default_encoding)

def compact_utf8_string(octets: str) -> bytes:
  return octets.encode('utf8')

def decompact_utf8_string(octets: bytes) -> str:
  return octets.decode('utf8')

iso_15962_compaction_schemes = {
  0b000: [compact_application_defined, decompact_application_defined], #As presented by the application
  0b001: [compact_integer, decompact_integer], #Integer
  0b010: [compact_numeric, decompact_numeric], #Numeric string (from “0” to “9”)
  0b011: [compact_5_bit, decompact_5_bit], #Uppercase alphabetic
  0b100: [compact_6_bit, decompact_6_bit], #Uppercase, numeric, etc.
  0b101: '7-bit code', #US ASCII
  0b110: [compact_octet_string, decompact_octet_string], #Unaltered 8 bit (default = ISO/IEC 8859-1)
  0b111: [compact_utf8_string, decompact_utf8_string], #External compaction to ISO/IEC 10646
}
