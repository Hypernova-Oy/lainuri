from logging_context import logging
log = logging.getLogger(__name__)

import helpers

class Tag():

  def __init__(self):
    self._antenna_id = None
    self._air_protocol_type_id = None
    self._tag_type_id = None
    self._serial_number = None
    self._tag_memory = None

  def antenna_id(self, antenna_id=None):
    if antenna_id: self._antenna_id = antenna_id
    if None == self._antenna_id: raise AttributeError(f"antenna_id not set for tag '{self.__dict__}'")
    return self._antenna_id

  def air_protocol_type_id(self, air_protocol_type_id=None):
    if air_protocol_type_id: self._air_protocol_type_id = air_protocol_type_id
    if None == self._air_protocol_type_id: raise AttributeError(f"air_protocol_type_id not set for tag '{self.__dict__}'")
    return self._air_protocol_type_id

  def tag_type_id(self, tag_type_id=None):
    if tag_type_id: self._tag_type_id = tag_type_id
    if None == self._tag_type_id: raise AttributeError(f"tag_type_id not set for tag '{self.__dict__}'")
    return self._tag_type_id

  def serial_number(self, serial_number=None):
    if serial_number: self._serial_number = serial_number
    if None == self._serial_number: raise AttributeError(f"serial_number not set for tag '{self.__dict__}'")
    return self._serial_number

  def tag_memory(self, tag_memory=None):
    if tag_memory: self._tag_memory = tag_memory
    if None == self._tag_memory: raise AttributeError(f"tag_memory not set for tag '{self.__dict__}'")
    return self._tag_memory

  def connected(self, handle: bytes):
    self._connected_handle = handle
    log.info(f"Connected as handle '{handle}' to tag '{self.__dict__}'")
