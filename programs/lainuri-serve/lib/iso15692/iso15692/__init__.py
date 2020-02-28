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
import re

import iso15692.compaction
import iso15692.format
from iso15692.util import ByteStream, DataObject

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

def get_data_object(tag_memory: ByteStream) -> DataObject:
  dob = DataObject()
  sequence = 0

  while (tag_memory.has_next()):
    sequence = sequence + 1
    # Skip null precursors
    while (tag_memory.peek() == 0x80):
      tag_memory.next()

    # Terminator precursor
    if tag_memory.peek() == 0x00:
      return dob

    precursor = get_precursor(tag_memory)

    if precursor['offset']:
      offset_length = tag_memory.next()
    else:
      offset_length = None

    length_of_compacted_data = iso15692.compaction.decode_compacted_object_length(tag_memory)
    compacted_data = tag_memory.slurp(length_of_compacted_data)

    if offset_length:
      offset_bytes = tag_memory.slurp(offset_length)
    else:
      offset_bytes = None
    print(precursor)
    dob.add_data_element(iso15692.util.DataElement(
      offset_bytes=offset_bytes,
      compaction_type_code=precursor['compaction_type_code'],
      object_identifier=precursor['object_identifier'],
      sequence=sequence,
      data=iso15692.compaction.get_decompaction_scheme(precursor['compaction_type_code'])(compacted_data),
      compacted_data=compacted_data,
      length_of_compacted_data=length_of_compacted_data,
    ))

  return dob

def get_precursor(tag_memory: ByteStream):
  precursor_byte = tag_memory.next()
  precursor = {
    'offset': (precursor_byte & 0b10000000) >> 7,
    'compaction_type_code': (precursor_byte & 0b01110000) >> 4,
    'object_identifier': precursor_byte & 0b00001111,
  }
  if precursor['object_identifier'] == 0b1111:
    precursor['object_identifier'] = precursor['object_identifier'] + tag_memory.next()
  return precursor
