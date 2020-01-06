#!/usr/bin/python3

import context

from RL866.iblock import IBlock_ReadSystemConfigurationBlock, IBlock_ReadSystemConfigurationBlock_Response, IBlock_TagInventory, IBlock_TagInventory_Response, IBlock_TagConnect, IBlock_TagConnect_Response
import RL866.state

def test_IBlock_ReadSystemConfigurationBlock():
  RL866.state.transmission_sequence_number = 0
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
  RL866.state.transmission_sequence_number = 1
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
  RL866.state.transmission_sequence_number = 1
  req = IBlock_TagConnect(tag)
  assert req.sof() == b'\xFA'
  assert req.len() == b'\x13'
  assert req.rid() == b'\xFF'
  assert req.pcb() == b'\x40'
  assert req.inf() == b'\x32\x00\x01\x01\x09\x01\xa7\x27\x38\x3f\x00\x01\x04\xe0'
  assert req.chk() == b'\xA3\xBF'
  assert req.pack() == b'\xfa\x13\xff\x40\x32\x00\x01\x01\x09\x01\xa7\x27\x38\x3f\x00\x01\x04\xe0\xa3\xbf'

  msg_response = b'\xfa\x09\x01\x40\x32\x00\x00\x01\xb2\x93'
  res = IBlock_TagConnect_Response(msg_response)
  assert res.pack() == msg_response
