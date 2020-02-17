from lainuri.config import get_config
from lainuri.logging_context import logging
log = logging.getLogger(__name__)

from typing import Callable

import lainuri.helpers as helpers
from lainuri.RL866.message import Message
from lainuri.RL866.tag import Tag
import lainuri.RL866.state

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
    log.info(f"TagMemoryAccessCommand ISO15693_ReadSingleBlock chosen. read_security_status='{read_security_status}', start_block_address='{start_block_address}'")
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

  def ISO15693_WriteSingleBlock(self, block_address: int, block_data: bytes):
    log.info(f"TagMemoryAccessCommand ISO15693_WriteSingleBlock chosen. block_address='{block_address}', block_data='{block_data}'")
    """
    Field 1.Block address:
      Data type: WORD
    Field 2.Block data
      Data type: BYTE[n]
    """
    self.command = helpers.int_to_word(0x0050)
    self.parameter = helpers.int_to_word(block_address) + block_data
    self.response_parser = self._no_response_parser
    return self

  def ISO15693_ReadMultipleBlocks(self, tag: Tag=None, read_security_status=1, start_block_address=0, number_of_blocks_to_read=16):
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
    if read_security_status: self.read_security_status = read_security_status
    if tag and tag.tag_memory_capacity_blocks: number_of_blocks_to_read = tag.tag_memory_capacity_blocks - start_block_address

    self.command = helpers.int_to_word(0x0003)
    self.parameter = helpers.int_to_byte(read_security_status) + \
                     helpers.int_to_word(start_block_address) + \
                     helpers.int_to_word(number_of_blocks_to_read)
    self.response_parser = self.ISO15693_ReadMultipleBlocks_ParseResponse
    return self

  def ISO15693_WriteMultipleBlocks(self, tag: Tag, start_block_address: int, number_of_blocks_to_write: int, blocks_data_bytes: bytes):
    log.info(f"TagMemoryAccessCommand ISO15693_WriteMultipleBlocks chosen. tag='{tag.serial_number()}', start_block_address='{start_block_address}', number_of_blocks_to_write='{number_of_blocks_to_write}', blocks_data_bytes='{blocks_data_bytes}'")
    """
    Field 1.Start block address:
      Data type: WORD
    Field 2.Number of blocks to write:
      Data type: WORD
    Field 3.Block data to write
      Data type: BYTE[n]
      n=Number of blocks * block size
    """
    if not tag.block_size: raise Exception(f"Tag.block_size not set for serial_number='{tag.serial_number()}'")
    block_size = tag.block_size
    expected_data_size = block_size * number_of_blocks_to_write

    if len(blocks_data_bytes) != expected_data_size:
      raise Exception(f"Writing multiple blocks to tag='{tag.serial_number()}' failed. Written bytes do not align with expected block size. number_of_blocks_to_write='{number_of_blocks_to_write}', expected bytes count='{expected_data_size}', tag block size='{block_size}', data to write='{blocks_data_bytes}'")

    self.command = helpers.int_to_word(0x0004)
    self.parameter = helpers.int_to_word(start_block_address) + \
                     helpers.int_to_word(number_of_blocks_to_write) + \
                     blocks_data_bytes + \
                     b'\x00' # For some reason the message needs to end in \x00, which doesn't look like it is documented.
    self.response_parser = self._no_response_parser
    return self

  def ISO15693_GetTagSystemInformation(self):
    log.info(f"TagMemoryAccessCommand ISO15693_GetTagSystemInformation chosen")
    """
    Parameter: None
    """
    self.command = helpers.int_to_word(0x000A)
    self.parameter = b''
    self.response_parser = self.ISO15693_GetTagSystemInformation_ParseResponse
    return self

  def ISO15693_Write_AFI(self, tag: Tag, byte: bytes):
    log.info(f"TagMemoryAccessCommand ISO15693_Write_AFI chosen")
    """
    Field 1.AFI:
      Data type:BYTE
    """
    self.command = helpers.int_to_word(0x0006)
    if len(byte) != 1:
      raise Exception(f"Writing AFI to tag='{tag.serial_number()}' input error. AFI is only 1 byte! Trying to write bytes '{byte}'")
    self.parameter = byte
    self.response_parser = self._no_response_parser
    return self

  def _eas_compliant(self, tag: Tag):
    if (not tag.air_protocol_type_id() == lainuri.RL866.state.AIR_PROTO_ISO15693) or \
       (not " SLI" in lainuri.RL866.state.supported_tag_types[tag.air_protocol_type_id()][tag.tag_type_id()]):
      raise Exception(f"EAS is supported only with SLI tag types. Uncompliant tag='{tag.__dict__}'")

  def ISO15693_Enable_EAS(self, tag: Tag):
    log.info(f"TagMemoryAccessCommand ISO15693_Enable_EAS chosen")
    self._eas_compliant(tag)
    self.command = helpers.int_to_word(0x000C)
    self.parameter = b''
    self.response_parser = self._no_response_parser
    return self

  def ISO15693_Disable_EAS(self, tag: Tag):
    log.info(f"TagMemoryAccessCommand ISO15693_Disable_EAS chosen")
    self._eas_compliant(tag)
    self.command = helpers.int_to_word(0x000D)
    self.parameter = b''
    self.response_parser = self._no_response_parser
    return self

  def ISO15693_EAS_Alarm(self, tag: Tag):
    log.info(f"TagMemoryAccessCommand ISO15693_EAS_Alarm chosen")
    self._eas_compliant(tag)
    self.command = helpers.int_to_word(0x000F)
    self.parameter = b''
    self.response_parser = self._no_response_parser
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
    response = {}
    self.response = response

    response['field1'] = message.field14[0:1]
    response['DSFID_present']            = 1 if (response['field1'][0] & 1<<0) else 0
    response['AFI_present']              = 1 if (response['field1'][0] & 1<<1) else 0
    response['tag_memory_info_present']  = 1 if (response['field1'][0] & 1<<2) else 0
    response['IC_reference_present']     = 1 if (response['field1'][0] & 1<<3) else 0

    response['field2'] = message.field14[1:9]
    response['uid'] = helpers.lower_byte_fo_to_int(response['field2'])

    response['field3'] = message.field14[9:10]
    response['dsfid'] = helpers.lower_byte_fo_to_int(response['field3'])

    response['field4'] = message.field14[10:11]
    response['afi'] = helpers.lower_byte_fo_to_int(response['field4'])

    response['field51'] = message.field14[11:12]
    response['tag_memory_capacity_blocks'] = helpers.lower_byte_fo_to_int(response['field51'])
    tag.tag_memory_capacity_blocks = response['tag_memory_capacity_blocks']
    response['field52'] = message.field14[12:13]
    response['block_size'] = helpers.lower_byte_fo_to_int(response['field52'])
    tag.block_size = response['block_size']

    response['field6'] = message.field14[13:14]
    response['ic_reference'] = helpers.lower_byte_fo_to_int(response['field6'])

    return response

  def ISO15693_ReadMultipleBlocks_ParseResponse(self, message: Message, tag: Tag):
    """
    Field 1.Number of blocks read:
      Data type: WORD
    Field 2.Data of blocks read:
      Data type: BYTE[n]
      When read security status is 0:
      n= Number of blocks read * Block size
      When read security status is 1:
      N= Number of blocks read * (Block size + security status (1Byte))
    """
    response = {}
    self.response = response

    response['field1'] = message.field14[0:2]
    response['number_blocks_read'] = helpers.word_to_int(response['field1'])

    block_size = tag.block_size if tag.block_size else 4
    response['field2'] = message.field14[2:block_size*response['number_blocks_read']+2]
    # Split the response to blocks of bytes
    response['data_of_blocks_read'] = []
    for i in range(0,response['number_blocks_read']): response['data_of_blocks_read'].append(response['field2'][i*block_size:(i+1)*block_size].hex())

    return response

  def _no_response_parser(self, message: Message, tag: Tag):
    if len(message.field14) != 0: raise Exception(f"Expected 0 bytes from response, but got bytes '{message.field14}'. Using command '{self}'")
    self.response = {}
    return self.response
