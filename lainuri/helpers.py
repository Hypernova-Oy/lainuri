from typing import Any, List
import math

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

def int_to_byte(intgr: int) -> bytes:
  return int_to_bytes(intgr, 1)

def int_to_word(intgr: int) -> bytes:
  return int_to_bytes(intgr, 2)

def int_to_dword(intgr: int) -> bytes:
  return int_to_bytes(intgr, 4)

def int_to_bytes(intgr: int, bytes_count: int = None) -> bytes:
  if not bytes_count:
    bytes_count = math.ceil(intgr.bit_length() / 8)
  return intgr.to_bytes(bytes_count, byteorder='little')

PRIMITIVE_TYPES = (int, float, complex, str, bool, type(None))
CONTAINER_TYPES = (dict, list, tuple, range)
def null_safe_lookup(obckt, keys: List, value: Any = None) -> Any:
  """
  As Python3 doesn't seem to have a null-safe nested map/dict lookup feature, here is my own.
  Given an Object or Dict, safely lookups a nested data structure
  """
  if isinstance(keys, str): keys = keys.split('.')
  try:
    if isinstance(obckt, CONTAINER_TYPES):
      if len(keys) == 1:
        if value != None:
          obckt[keys[0]] = value
          return obckt[keys[0]]
        else:
          return obckt[keys[0]]
      return null_safe_lookup(obckt.get(keys[0], None), keys[1:])
    elif hasattr(obckt, '__dict__'):  # with a high probability this is a class instance or a class object
      if len(keys) == 1:
        if value != None:
          obckt[keys[0]] = value
          return getattr(obckt, keys[0])
        else:
          return getattr(obckt, keys[0])
      return null_safe_lookup(getattr(obckt, keys[0]), keys[1:])
    elif isinstance(obckt, PRIMITIVE_TYPES):
      return None
    else:
      raise LookupError(f"Object/Dict '{obckt}' is not a dict or object? Cannot look for keys='{keys}'")
  except IndexError:  # Accesing 0-length lists or similar raises this type of exception. We can just conclude that None is found
    return None
