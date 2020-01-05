#!/usr/bin/python3

import pdb

import context

from RL866.message import Message2

def test_Message2():
  msg_response = b'\xFA\x05\x01\xE0\x58\xFE'
  msg = Message2(msg_response)
  assert msg.SOF == b'\xFA'
  assert msg.CHK == b'\x58\xFE'
  assert msg.INF == b''

  msg_response = b'\xfa\x08\xff\x00\x01\x81\x0f\x4d\xeb'
  msg = Message2(msg_response)
  assert msg.SOF == b'\xFA'
  assert msg.CHK == b'\x4D\xEB'
  assert msg.INF == b'\x01\x81\x0F'

