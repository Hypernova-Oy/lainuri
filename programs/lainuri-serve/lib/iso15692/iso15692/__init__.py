# coding: utf-8

# ISO 15692 compaction
# Copyright (C) 2020 Olli-Antti Kivilahti @ Hypernova Oy
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
#

from bitarray import bitarray, frozenbitarray
import logging
from pprint import pformat
import re

import iso15692.compaction
import iso15692.format

log = logging.getLogger(__name__)

"""
Overload this from your program to set the known data element types for the default vocabulary for relative object identifiers (OID).
Without this, resolving data elements with relative OID references cannot succeed.

eg.
iso15692.relative_data_element_types = iso28560.data_element_types
"""
relative_data_element_types = {
  1: {
    'name': 'Primary item identifier',
    'status': 'Mandatory',
    'format': iso15692.format.IRV,
    'lock': 'should',
  }
}

def set_application_defined_compaction_scheme(compaction_func: callable, decompaction_func: callable):
  iso15692.compaction.application_defined_compaction_scheme = [compaction_func, decompaction_func]



class ByteStream():
  def __init__(self, byttes: bytes):
    self.byttes = byttes
    self.i = -1

#  def __repr__(self):
#    if self.i < 0:
#      return '|' + self.byttes.hex()
#    return f"ByteStream():> byttes='{self.byttes[0:self.i].hex() + '|' + self.byttes[self.i:self.i+1].hex() + '|' + self.byttes[self.i+1:].hex()}' i='{self.i}' len='{len(self.byttes)}'"

  def current(self):
    return self.byttes[self.i]

  def has_next(self):
    return True if len(self.byttes) > self.i+1 else False

  def next(self):
    self.i = self.i + 1
    return self.byttes[self.i]

  def peek(self):
    return self.byttes[self.i+1]

  def previous(self):
    self.i = self.i - 1
    return self.byttes[self.i]

  def slurp(self, n: int):
    byttes = self.byttes[self.i+1 : self.i+n+1]
    self.i = self.i + n
    return byttes



class DataElement():
  def __init__(self, offset_bytes, compaction_type_code, object_identifier, data, compacted_data, length_of_compacted_data):
    self.offset_bytes=offset_bytes,
    self.compaction_type_code=compaction_type_code
    self.object_identifier=object_identifier
    self.sequence=None
    self.data=data
    self.compacted_data=compacted_data,
    self.length_of_compacted_data=length_of_compacted_data,
  def __repr__(self):
    return pformat(self.__dict__)



class DataObject():
  def __init__(self, tag_memory: bytes = None):
    self.data_elements = []
    self._tag_memory = ByteStream(tag_memory) if tag_memory else None

  def __repr__(self):
    return pformat(self.__dict__)

  def add_data_element(self, data_element: DataElement):
    self.data_elements.append(data_element)
    data_element.sequence = len(self.data_elements)
    return data_element

  def get_data_element(self, oid: int) -> DataElement:
    for de in self.data_elements:
      if de.object_identifier == oid:
        return de
    return None

  def decode(self, tag_memory: bytes = None):
    self._tag_memory = ByteStream(tag_memory) if tag_memory else self._tag_memory

    while (self._tag_memory.has_next()):
      # Skip null precursors
      while (self._tag_memory.peek() == 0x80):
        self._tag_memory.next()

      # Terminator precursor
      if self._tag_memory.peek() == 0x00:
        return self

      self.decode_next_data_element()

    return self

  def decode_next_data_element(self) -> DataElement:
    # Skip null precursors
    if (self._tag_memory.peek() == 0x80):
      raise Exception(f"Decoding next data element failed, precursor is NULL! tag_memory='{self._tag_memory}', dob='{self}'")

    # Terminator precursor
    if self._tag_memory.peek() == 0x00:
      raise Exception(f"Decoding next data element failed, precursor is TERMINATOR! tag_memory='{self._tag_memory}', dob='{self}'")

    precursor = self.get_precursor()

    if precursor['offset']:
      offset_length = self._tag_memory.next()
    else:
      offset_length = None

    length_of_compacted_data = iso15692.compaction.decode_compacted_object_length(self._tag_memory)
    compacted_data = self._tag_memory.slurp(length_of_compacted_data)

    if offset_length:
      offset_bytes = self._tag_memory.slurp(offset_length)
    else:
      offset_bytes = None

    return self.add_data_element(DataElement(
      offset_bytes=offset_bytes,
      compaction_type_code=precursor['compaction_type_code'],
      object_identifier=precursor['object_identifier'],
      data=iso15692.compaction.get_decompaction_scheme(precursor['compaction_type_code'])(compacted_data),
      compacted_data=compacted_data,
      length_of_compacted_data=length_of_compacted_data,
    ))

  def get_precursor(self):
    precursor_byte = self._tag_memory.next()
    precursor = {
      'offset': (precursor_byte & 0b10000000) >> 7,
      'compaction_type_code': (precursor_byte & 0b01110000) >> 4,
      'object_identifier': precursor_byte & 0b00001111,
    }
    if precursor['object_identifier'] == 0b1111:
      precursor['object_identifier'] = precursor['object_identifier'] + self._tag_memory.next()
    return precursor

