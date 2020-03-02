#!/usr/bin/python3

import context

import lainuri.RL866
from lainuri.RL866.CRC16 import crc16

def test_crc16():
  crc = crc16(
    bytes([
    #  0xFA, # SOF Start byte of frame
      0x08,
      0xFF,
      0x00,
      0x01,
      0x01,
      0x01,
    #  0xFF, # Expected checksum WORD
    #  0x8E,
    ])
  )
  assert crc == b'\xFF\x8E'

  crc = crc16(
    bytes([
    #  0xFA, # SOF Start byte of frame
      0x08,
      0xFF,
      0x40,
      0x01,
      0x02,
      0x01,
    #  0x20, # Expected checksum WORD
    #  0xB2,
    ])
  )
  assert crc == b'\x20\xB2'

  crc = crc16(
    bytes([
    #  0xFA, # SOF Start byte of frame
      0x17,
      0x01,
      0x00,
      0x01,
      0x00,
      0x00,
      0x01,
      0x01,
      0x02,
      0x02,
      0x00,
      0x03,
      0x01,
      0x64,
      0x00,
      0x00,
      0x00,
      0x00,
      0x00,
      0x00,
      0x00,
    #  0xC0, # Expected checksum WORD
    #  0x95,
    ])
  )
  assert crc == b'\xC0\x95'

def test_resynch():
  crc = crc16(
    bytes([
    #  0xFA, # SOF Start byte of frame
      0x05,
      0xFF,
      0xC0,
    #  0x20, # Expected checksum WORD
    #  0xB2,
    ])
  )
  assert crc == b'\x42\x39'
