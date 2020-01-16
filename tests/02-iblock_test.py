#!/usr/bin/python3

import context

from lainuri.RL866.iblock import IBlock_ReadSystemConfigurationBlock, IBlock_ReadSystemConfigurationBlock_Response, IBlock_TagInventory, IBlock_TagInventory_Response, IBlock_TagConnect, IBlock_TagConnect_Response, IBlock_TagDisconnect, IBlock_TagDisconnect_Response, IBlock_TagMemoryAccess, IBlock_TagMemoryAccess_Response
import lainuri.RL866.state as state
from lainuri.RL866.tag_memory_access_command import TagMemoryAccessCommand

def test_IBlock_ReadSystemConfigurationBlock():
  state.transmission_sequence_number = 0
  req = IBlock_ReadSystemConfigurationBlock(read_ROM=0, read_blocks=1)
  assert req.sof() == b'\xFA'
  assert req.len() == b'\x08'
  assert req.rid() == b'\xFF'
  assert req.pcb() == b'\x00'
  assert req.inf() == b'\x01\x01\x01'
  assert req.chk() == b'\xFF\x8E'
  assert req.pack() == b'\xFA\x08\xFF\x00\x01\x01\x01\xFF\x8E'

  #import pdb; pdb.set_trace()
  msg_response = b'\xFA\x17\x01\x00\x01\x00\x00\x01\x01\x02\x02\x00\x03\x01\x64\x00\x00\x00\x00\x00\x00\x00\xC0\x95'
  res = IBlock_ReadSystemConfigurationBlock_Response(msg_response)
  assert res.pack() == msg_response

  req = IBlock_ReadSystemConfigurationBlock(read_ROM=1, read_blocks=15)
  assert req.sof() == b'\xFA'
  assert req.len() == b'\x08'
  assert req.rid() == b'\xFF'
  assert req.pcb() == b'\x40'
  assert req.inf() == b'\x01\x81\x0F'
  assert req.chk() == b'\xFA\xFD'
  assert req.pack() == b'\xFA\x08\xFF\x40\x01\x81\x0F\xFA\xFD'

  msg_response = b'\xfa\x6b\x01\x40\x01\x00\x00\x07\x01\x02\x02\x00\x03\x01\x64\x00\x00\x00\x00\x00\x00\x00\x00\x09\x00\xff\x00\x10\x07\x13\x01\x0e\x08\x09\x0b\x00\x00\x00\x00\xe8\x03\x00\x00\x00\x00\x43\x83\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01\x00\x03\x00\x00\x01\x00\x00\x00\x01\x00\x01\x00\x00\x00\x00\x00\x00\x06\x00\x00\x00\x00\x00\x00\x00\x00\x00\x30\xb0'
  res = IBlock_ReadSystemConfigurationBlock_Response(msg_response)
  assert res.pack() == msg_response

tag = None
def test_IBlock_TagInventory():
  state.transmission_sequence_number = 1
  req = IBlock_TagInventory()
  assert req.sof() == b'\xFA'
  assert req.len() == b'\x07'
  assert req.rid() == b'\xFF'
  assert req.pcb() == b'\x40'
  assert req.inf() == b'\x31\x00'
  assert req.chk() == b'\x8al'
  assert req.pack() == b'\xfa\x07\xff\x40\x31\x00\x8a\x6c'

  msg_response = b'\xfa\x33\x01\x00\x31\x00\x00\x00\x03\x00\x03\x0e\x01\x01\x09\xa7\x27\x38\x3f\x00\x01\x04\xe0\x00\x0e\x01\x01\x09\x24\x26\x38\x3f\x00\x01\x04\xe0\x00\x0e\x01\x01\x09\xa4\x25\x38\x3f\x00\x01\x04\xe0\x00\x97\xff'
  res = IBlock_TagInventory_Response(msg_response)
  assert res.pack() == msg_response
  global tag
  tag = res.tags[0]

def test_IBlock_TagConnect():
  state.transmission_sequence_number = 1
  req = IBlock_TagConnect(tag)
  assert req.sof() == b'\xFA'
  assert req.len() == b'\x13'
  assert req.rid() == b'\xFF'
  assert req.pcb() == b'\x40'
  assert req.inf() == b'\x32\x00\x01\x01\x09\x01\xa7\x27\x38\x3f\x00\x01\x04\xe0'
  assert req.chk() == b'\xA3\xBF'
  assert req.pack() == b'\xfa\x13\xff\x40\x32\x00\x01\x01\x09\x01\xa7\x27\x38\x3f\x00\x01\x04\xe0\xa3\xbf'

  msg_response = b'\xfa\x09\x01\x40\x32\x00\x00\x01\xb2\x93'
  res = IBlock_TagConnect_Response(msg_response, tag)
  assert res.pack() == msg_response

def test_IBlock_TagMemoryAccess__ISO15693_GetTagSystemInformation():
  state.transmission_sequence_number = 1
  mac = TagMemoryAccessCommand().ISO15693_GetTagSystemInformation()
  req = IBlock_TagMemoryAccess(tag, mac)
  assert req.inf()  == b'\x34\x01\x02\x0a\x00'
  assert req.pack() == b'\xfa\x0a\xff\x40\x34\x01\x02\x0a\x00\x99\x7b'

  msg_response = b'\xfa\x1a\x01\x40\x34\x00\x00\x11\x0a\x00\x01\x0f\xa7\x27\x38\x3f\x00\x01\x04\xe0\x00\x00\x1b\x03\x01\x20\xe7'
  res = IBlock_TagMemoryAccess_Response(msg_response, tag, mac)
  assert res.pack() == msg_response

def test_IBlock_TagMemoryAccess__ISO15693_WriteMultipleBlocks():
  state.transmission_sequence_number = 1
  mac = TagMemoryAccessCommand().ISO15693_WriteMultipleBlocks(
    tag=tag,
    start_block_address=12,
    number_of_blocks_to_write=1,
    blocks_data_bytes=b'\x36\x37\x38',
  )
  req = IBlock_TagMemoryAccess(tag, mac)
  assert req.pack() == b'\xfa\x12\xff\x40\x34\x01\x0a\x04\x00\x0c\x00\x01\x00\x36\x37\x38\x00\xa2\xdd'

  mac = TagMemoryAccessCommand().ISO15693_ReadMultipleBlocks(
    read_security_status=0,
    start_block_address=12,
    number_of_blocks_to_read=1
  )
  msg_response = b'\xfa\x12\x01\x00\x34\x00\x00\x09\x03\x00\x01\x01\x00\x36\x37\x38\x00\x57\x29'
  res = IBlock_TagMemoryAccess_Response(msg_response, tag, mac)
  assert res.pack() == msg_response

def test_IBlock_TagDisconnect():
  state.transmission_sequence_number = 0
  req = IBlock_TagDisconnect(tag)
  assert req.sof() == b'\xFA'
  assert req.len() == b'\x07'
  assert req.rid() == b'\xFF'
  assert req.pcb() == b'\x00'
  assert req.inf() == b'\x33\x01'
  assert req.chk() == b'\xc5\x48'
  assert req.pack() == b'\xfa\x07\xff\x00\x33\x01\xc5\x48'

  msg_response = b'\xfa\x08\x01\x00\x33\x00\x00\xa6\x4b'
  res = IBlock_TagDisconnect_Response(msg_response, tag)
  assert res.pack() == msg_response
