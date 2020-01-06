from logging_context import logging
log = logging.getLogger(__name__)

def _two_way_link_dict(d) -> dict:
  tmp = dict()
  for k in d:
    tmp[d[k]] = k
    tmp[k] = d[k]
  return tmp

def shift_byte(buffer: bytearray, iterator: list) -> bytearray:
  iterator[0] += 1 # Increment the reference to the iterator
  return buffer[ iterator[0]-1 : iterator[0] ] # Get the next byte

def shift_bytes(buffer: bytearray, iterator: list, count: int) -> bytearray:
  iterator[0] += count # Increment the reference to the iterator
  return buffer[ iterator[0]-count : iterator[0] ] # Get the next bytes

def shift_word(buffer: bytearray, iterator: list) -> bytearray:
  iterator[0] += 2
  return buffer[ iterator[0]-2 : iterator[0] ] # Get the next two bytes

def shift_dword(buffer: bytearray, iterator: list) -> bytearray:
  iterator[0] += 4
  return buffer[ iterator[0]-4 : iterator[0] ] # Get the next four bytes

def word_to_int(bs: bytes) -> int:
  if len(bs) != 2: raise Exception("word_to_int(bs):> WORD is not 2 bytes!")
  return lower_byte_fo_to_int(bs)

def dword_to_int(bs: bytes) -> int:
  if len(bs) != 4: raise Exception("dword_to_int(bs):> DWORD is not 2 bytes!")
  return lower_byte_fo_to_int(bs)

def lower_byte_fo_to_int(bs: bytes) -> int:
  """
  Multibyte fields are "inverted" when they come out of the connection.
  They are lower byte first out.

  3.Data Type Description
  Type      Description
  BYTE      8-bit data, the value range 00h-FFh
  WORD      16-bit data, the value range 0000h-FFFFh,Lower byte first out
  DWORD     32-bit data, the value range00000000h-FFFFFFFFh,Lower byte first out
  BYTE[ n ] Array type, It consists of many of BYTE types
  EBV # TODO: EBV looks like a big mess
  """
  return int.from_bytes(bs, 'little')
