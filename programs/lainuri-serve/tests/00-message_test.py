#!/usr/bin/python3

import context

from lainuri.RL866.message import Message, parseMessage
import lainuri.helpers as helpers


def test_Message2():
  msg = Message()
  msg_response = b'\xFA\x05\x01\xE0\x58\xFE'
  parseMessage(msg, msg_response)
  assert msg.SOF == b'\xFA'
  assert msg.CHK == b'\x58\xFE'
  assert msg.INF == b''

  msg = Message()
  msg_response = b'\xfa\x08\xff\x00\x01\x81\x0f\x4d\xeb'
  parseMessage(msg, msg_response)
  assert msg.SOF == b'\xFA'
  assert msg.CHK == b'\x4D\xEB'
  assert msg.INF == b'\x01\x81\x0F'

def test_lower_byte_first_out_to_int():
  assert helpers.word_to_int(b'\xFF\x00') == 255
  assert helpers.dword_to_int(b'\x01\x02\x03\x04') == 67305985
  assert helpers.lower_byte_fo_to_int(b'\x01\x02\x03') == 197121
