from logging_context import logging
log = logging.getLogger(__name__)

from typing import Callable

import helpers
from RL866.message import Message
from RL866.tag import Tag

EXPECTED_NO_BYTES = 0
EXPECTED_MULTIPLE_BYTES = 255

class TagMemoryAccessCommand():
  """
  6.5.Tag memory access command
  """

  tag_type: int = None
  command = b''
  parameter = b''
  response_parser: Callable = None

  def __init__(self):
    pass

  def len(self) -> int:
    if not self.command: raise Exception(f"Requesting to len() TagMemoryAccessCommand-object, which doesn't have it's command set?")
    return len(self.command) + len(self.parameter)

  def ISO15693_Reset(self):
    log.info(f"TagMemoryAccessCommand ISO15693_Reset chosen")
    self.command = helpers.int_to_word(0x0001)
    self.parameter = b''
    self.response_parser = self._no_response_parser
    return self

  def ISO15693_Select(self):
    log.info(f"TagMemoryAccessCommand ISO15693_Select chosen")
    """
    Note: This command only support addressed mode
    """
    self.command = helpers.int_to_word(0x0002)
    self.parameter = b''
    self.response_parser = self._no_response_parser
    return self

  def ISO15693_ReadSingleBlock(self, read_security_status=1, start_block_address=0):
    log.info(f"TagMemoryAccessCommand ISO15693_ReadSingleBlock chosen")
    """
    Field 1.Whether to read security status of data block:
      Data type :BYTE;
      0: Security status not as a part of a block data.
      1: Security status as a part of a block data.
    Field 2.Start block address:
      Data type:WORD
    """
    self.command = helpers.int_to_word(0x004F)
    self.parameter = bytes([read_security_status]) + helpers.int_to_word(start_block_address)
    self.expected_result_bytes = EXPECTED_MULTIPLE_BYTES
    return self

  def ISO15693_WriteSingleBlock(self, block_address, block_data):
    log.info(f"TagMemoryAccessCommand ISO15693_WriteSingleBlock chosen")
    """
    Field 1.Block address:
      Data type: WORD
    Field 2.Block data
      Data type: BYTE[n]
    """
    self.command = helpers.int_to_word(0x0050)
    self.parameter = helpers.int_to_word(block_address) + helpers.int_to_bytes(block_data)
    self.response_parser = self._no_response_parser
    return self

  def ISO15693_ReadMultipleBlocks(self, read_security_status=1, start_block_address=0, number_of_blocks_to_read=16):
    log.info(f"TagMemoryAccessCommand ISO15693_ReadMultipleBlocks chosen")
    """
    Field 1.Read security status
      Data type: BYTE;
      Whether to read block security status not or .
      0: Not read
      1: Read
    Field 2.Start block address:
      Data type: WORD
    Field 3.Number of blocks to read:
      Data type: WORD
    """
    self.command = helpers.int_to_word(0x0003)
    self.parameter = helpers.int_to_byte(read_security_status) + \
                     helpers.int_to_word(start_block_address) + \
                     helpers.int_to_word(number_of_blocks_to_read)
    self.expected_result_bytes = EXPECTED_MULTIPLE_BYTES
    return self

  def ISO15693_GetTagSystemInformation(self):
    log.info(f"TagMemoryAccessCommand ISO15693_GetTagSystemInformation chosen")
    """
    Field 1.Start block address:
      Data type: WORD
    Field 2.Number of blocks to write:
      Data type: WORD
    Field 3.Block data to write
      Data type: BYTE[n]
      n=Number of blocks * block size
    """
    self.command = helpers.int_to_word(0x000A)
    self.parameter = b''
    self.response_parser = self.ISO15693_GetTagSystemInformation_ParseResponse
    return self

  def ISO15693_(self):
    log.info(f"TagMemoryAccessCommand ISO15693_ chosen")
    self.command = helpers.int_to_word(0x0004)
    self.parameter = b''
    self.response_parser = self._no_response_parser
    return self

  def ISO15693_GetTagSystemInformation_ParseResponse(self, message: Message, tag: Tag):
    """
    Field 1.Flag:
      Data type: BYTE;
      b0: DSFID is present when this bit set to 1.
      b1: AFI is present when this bit set to 1;
      b2: Tag memory information is present when this bit set to 1;
      b3: IC reference is present when this bit set to 1;
    Field 2.UID:
      Data type: BYTE[8];
    Field 3.DSFID:
      Data type: BYTE;
    Field 4.AFI:
      Data type: BYTE ;
    Field 5.Tag memory information
      Memory capacity = Number of blocks* Block size
      Field 5.1.Number of blocks:
        Data type: BYTE ;
      Field 5.2.Block size:
        Data type: BYTE;
    Field 6.IC reference
      Data type: BYTE;
    """
    self.field1 = message.field14[0:1]
    self.DSFID_present            = self.field1[0] & 1<<0
    self.AFI_present              = self.field1[0] & 1<<1
    self.tag_memory_info_present  = self.field1[0] & 1<<2
    self.IC_reference_present     = self.field1[0] & 1<<3

    self.field2 = message.field14[1:9]
    self.uid = helpers.lower_byte_fo_to_int(self.field2)

    self.field3 = message.field14[9:10]
    self.dsfid = helpers.lower_byte_fo_to_int(self.field3)

    self.field4 = message.field14[10:11]
    self.afi = helpers.lower_byte_fo_to_int(self.field4)

    self.field51 = message.field14[11:12]
    self.tag_memory_capacity_blocks = helpers.lower_byte_fo_to_int(self.field51)
    tag.tag_memory_capacity_blocks = self.tag_memory_capacity_blocks
    self.field52 = message.field14[12:13]
    self.block_size = helpers.lower_byte_fo_to_int(self.field52)
    tag.block_size = self.block_size

    self.field6 = message.field14[13:14]
    self.ic_reference = helpers.lower_byte_fo_to_int(self.field6)

  def _no_response_parser(self, message: Message, tag: Tag):
    if len(message.field14) != 0: raise Exception(f"Expected 0 bytes from response, but got bytes '{message.field14}'. Using command '{self.__dict__}'")
