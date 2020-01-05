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
