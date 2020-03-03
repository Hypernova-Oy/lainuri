from lainuri.config import get_config
from lainuri.logging_context import logging
log = logging.getLogger(__name__)

import lainuri.RL866.state

import iso28560
import re
import yaml


class Tag():

  eval_security_regex = re.compile('^[0-9A-Za-z_-]+$')

  def __init__(self, serial_number: str = None):
    self._afi = None
    self._air_protocol_type_id = None
    self._antenna_id = None
    self._block_size = None
    self._connected_handle = None
    self._dsfid = None
    self._memory_capacity_blocks = None
    self._primary_item_identifier = None
    self._serial_number = serial_number
    self._tag_memory = None
    self._tag_type_id = None

  def __repr__(self):
    return f"{self.__class__} at {id(self)}:> afi='{self._afi}' dsfid='{self._dsfid}' serial_number='{self._serial_number}'" + \
      f" pii='{self._primary_item_identifier}'" if self._primary_item_identifier else ''

  def __dump__(self):
    return yaml.dump({'!type': self.__class__, '!id': hex(id(self)), **self.__dict__})

  def afi(self, afi: int = None) -> int:
    if afi != None: self._afi = afi
    if self._afi == None: raise AttributeError(f"ISO15693_GetTagSystemInformation not invoked for this tag '{self.__dict__}'")
    return self._afi

  def dsfid(self, dsfid: int = None) -> int:
    if dsfid != None: self._dsfid = dsfid
    if self._dsfid == None: raise AttributeError(f"ISO15693_GetTagSystemInformation not invoked for this tag '{self.__dict__}'")
    return self._dsfid

  def block_size(self, block_size: int = None) -> int:
    if block_size != None: self._block_size = block_size
    if self._block_size == None: raise AttributeError(f"ISO15693_GetTagSystemInformation not invoked for this tag '{self.__dict__}'")
    return self._block_size

  def memory_capacity_blocks(self, memory_capacity_blocks: int = None) -> int:
    if memory_capacity_blocks != None: self._memory_capacity_blocks = memory_capacity_blocks
    if self._memory_capacity_blocks == None: raise AttributeError(f"ISO15693_GetTagSystemInformation not invoked for this tag '{self.__dict__}'")
    return self._memory_capacity_blocks

  def antenna_id(self, antenna_id=None):
    if antenna_id != None: self._antenna_id = antenna_id
    if None == self._antenna_id: raise AttributeError(f"antenna_id not set for tag '{self.__dict__}'")
    return self._antenna_id

  def air_protocol_type_id(self, air_protocol_type_id=None):
    if air_protocol_type_id != None: self._air_protocol_type_id = air_protocol_type_id
    if None == self._air_protocol_type_id: raise AttributeError(f"air_protocol_type_id not set for tag '{self.__dict__}'")
    return self._air_protocol_type_id

  def tag_type_id(self, tag_type_id=None):
    if tag_type_id != None: self._tag_type_id = tag_type_id
    if None == self._tag_type_id: raise AttributeError(f"tag_type_id not set for tag '{self.__dict__}'")
    return self._tag_type_id

  def get_tag_type(self) -> str:
    return lainuri.RL866.state.supported_tag_types[self.air_protocol_type_id()][self.tag_type_id()]

  def serial_number(self, serial_number=None):
    if serial_number: self._serial_number = serial_number
    if None == self._serial_number: raise AttributeError(f"serial_number not set for tag '{self.__dict__}'")
    return self._serial_number

  def tag_memory(self, tag_memory=None):
    if tag_memory: self._tag_memory = tag_memory
    if None == self._tag_memory: raise AttributeError(f"ISO15693_ReadMultipleBlocks or similar not invoked for this tag '{self.__dict__}'")
    return self._tag_memory

  def connect(self, handle: bytes):
    self._connected_handle = handle
    log.info(f"Connected as handle '{handle}' to tag '{self.__dict__}'")

  def disconnect(self):
    log.info(f"Disconnected old handle '{self._connected_handle}' to tag '{self.__dict__}'")
    self._connected_handle = None

  def get_connection_handle(self) -> bytes:
    return self._connected_handle

  def validate(self):
    if not lainuri.RL866.state.supported_tag_types[self.air_protocol_type_id()][self.tag_type_id()]:
      raise Exception(f"Tag serial_number='{self.serial_number()}', air_protocol_type_id='{self.air_protocol_type_id()}', tag_type_id='{self.tag_type_id()}' is not a supported tag type for the given air protocol")


  def to_ui(self):
    return {
      'tag_type': 'rfid',
      'tag_model': self.get_tag_type(),
    }


  ## ISO 15692 / ISO 25680 commands
  def get_data_object_format_implementation(self):
    overloads = get_config('devices.rfid-reader.iso28560-data-format-overloads')
    if overloads:
      for ol in overloads:
        for key in ol.keys():
          if key == "!class": continue
          attr = getattr(self, key, None)
          if isinstance(attr, type(self.get_data_object_format_implementation)): # If attr is a function
            if attr() == ol[key]:
              dob_class = self._get_data_object_format_implementation_class_from_string(ol['!class'])
              log.info(f"ISO28560 data format overloaded. Tag='{self.serial_number()}' impl='{dob_class}'")
              return dob_class
    return iso28560._get_data_object_class(self.dsfid())

  def _get_data_object_format_implementation_class_from_string(self, name):
    if self.eval_security_regex.search(name):
      return eval('iso28560.' + name)
    else:
      raise ValueError(f"class name '{name}' doesn't match allowed eval security scope '{self.eval_security_regex}'")

  def iso25680_get_primary_item_identifier(self):

    if self._primary_item_identifier:
      return self._primary_item_identifier

    self.dob = self.get_data_object_format_implementation()(
      afi=self.afi(),
      dsfid=self.dsfid(),
      block_size=self.block_size(),
      memory_capacity_blocks=self.memory_capacity_blocks(),
      tag_memory=self.tag_memory()
    )

    self._primary_item_identifier = self.dob.get_primary_item_identifier()
    return self._primary_item_identifier
