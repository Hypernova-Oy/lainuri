#!/usr/bin/python3

import context

from RL866.iblock import IBlock_ReadSystemConfigurationBlock, IBlock_ReadSystemConfigurationBlock_Response, IBlock_TagInventory
import RL866.state

def test_IBlock_ReadSystemConfigurationBlock():
  RL866.state.transmission_sequence_number = 0
  msg_request = IBlock_ReadSystemConfigurationBlock(read_ROM=0, read_blocks=1)
  assert msg_request.sof() == b'\xFA'
  assert msg_request.len() == b'\x08'
  assert msg_request.rid() == b'\xFF'
  assert msg_request.pcb() == b'\x00'
  assert msg_request.inf() == b'\x01\x01\x01'
  assert msg_request.chk() == b'\xFF\x8E'
  assert msg_request.pack() == b'\xFA\x08\xFF\x00\x01\x01\x01\xFF\x8E'

  #import pdb; pdb.set_trace()
  msg_response = b'\xFA\x17\x01\x00\x01\x00\x00\x01\x01\x02\x02\x00\x03\x01\x64\x00\x00\x00\x00\x00\x00\x00\xC0\x95'
  res = IBlock_ReadSystemConfigurationBlock_Response(msg_response)
  assert res.pack() == msg_response

  msg_request = IBlock_ReadSystemConfigurationBlock(read_ROM=1, read_blocks=15)
  assert msg_request.sof() == b'\xFA'
  assert msg_request.len() == b'\x08'
  assert msg_request.rid() == b'\xFF'
  assert msg_request.pcb() == b'\x40'
  assert msg_request.inf() == b'\x01\x81\x0F'
  assert msg_request.chk() == b'\xFA\xFD'
  assert msg_request.pack() == b'\xFA\x08\xFF\x40\x01\x81\x0F\xFA\xFD'

  msg_response = b'\xfa\x6b\x01\x40\x01\x00\x00\x07\x01\x02\x02\x00\x03\x01\x64\x00\x00\x00\x00\x00\x00\x00\x00\x09\x00\xff\x00\x10\x07\x13\x01\x0e\x08\x09\x0b\x00\x00\x00\x00\xe8\x03\x00\x00\x00\x00\x43\x83\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01\x00\x03\x00\x00\x01\x00\x00\x00\x01\x00\x01\x00\x00\x00\x00\x00\x00\x06\x00\x00\x00\x00\x00\x00\x00\x00\x00\x30\xb0'
  res = IBlock_ReadSystemConfigurationBlock_Response(msg_response)
  assert res.pack() == msg_response

def test_IBlock_TagInventory():
  RL866.state.transmission_sequence_number = 1
  msg_request = IBlock_TagInventory()
  assert msg_request.sof() == b'\xFA'
  assert msg_request.len() == b'\x07'
  assert msg_request.rid() == b'\xFF'
  assert msg_request.pcb() == b'\x40'
  assert msg_request.inf() == b'\x31\x00'
  assert msg_request.chk() == b'\x8al'
  assert msg_request.pack() == b'\xfa\x07\xff\x40\x31\x00\x8a\x6c'
