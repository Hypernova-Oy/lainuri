#!/usr/bin/python3

import context

from RL866.sblock import SBlock_RESYNC, SBlock_RESYNC_Response 

def test_SBlock_RESYNC():
  msg_request = SBlock_RESYNC()
  assert msg_request.pack() == b'\xFA\x05\xFF\xC0\x42\x39'

  msg_response = b'\xFA\x05\x01\xE0\x58\xFE'
  res = SBlock_RESYNC_Response(msg_response)
  assert res.pack() == msg_response
