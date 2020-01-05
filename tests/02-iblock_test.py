#!/usr/bin/python3

import context

from RL866.iblock import IBlock_ReadSystemConfigurationBlock, IBlock_ReadSystemConfigurationBlock_Response

def test_IBlock_ReadSystemConfigurationBlock():
  msg_request = IBlock_ReadSystemConfigurationBlock(readROM=0, readBytes=1)
  assert msg_request.sof() == b'\xFA'
  assert msg_request.len() == b'\x08'
  assert msg_request.rid() == b'\xFF'
  assert msg_request.pcb() == b'\x00'
  assert msg_request.inf() == b'\x01\x01\x01'
  assert msg_request.chk() == b'\xFF\x8E'
  assert msg_request.pack() == b'\xFA\x08\xFF\x00\x01\x01\x01\xFF\x8E'

  msg_response = b'\xFA\x17\x01\x00\x01\x00\x00\x01\x01\x02\x02\x00\x03\x01\x64\x00\x00\x00\x00\x00\x00\x00\xC0\x95'
  res = IBlock_ReadSystemConfigurationBlock_Response(msg_response)
  assert res.pack() == msg_response

  msg_request = IBlock_ReadSystemConfigurationBlock(readROM=1, readBytes=15)
  assert msg_request.sof() == b'\xFA'
  assert msg_request.len() == b'\x08'
  assert msg_request.rid() == b'\xFF'
  assert msg_request.pcb() == b'\x00'
  assert msg_request.inf() == b'\x01\x81\x0F'
  assert msg_request.chk() == b'M\xEB'
  assert msg_request.pack() == b'\xFA\x08\xFF\x00\x01\x81\x0FM\xEB'

  msg_response = b'\xFA\x05\x01\xE0\x58\xFE'
  res = IBlock_ReadSystemConfigurationBlock_Response(msg_response)
  assert res.pack() == msg_response
