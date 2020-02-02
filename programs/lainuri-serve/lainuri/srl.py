#!/usr/bin/python3

import serial
import time

from logging_context import logging
from RL866.sblock import SBlock_RESYNC, SBlock_RESYNC_Response
from RL866.iblock import IBlock_ReadSystemConfigurationBlock, IBlock_ReadSystemConfigurationBlock_Response, IBlock_TagInventory, IBlock_TagInventory_Response, IBlock_TagConnect, IBlock_TagConnect_Response, IBlock_TagDisconnect, IBlock_TagDisconnect_Response, IBlock_TagMemoryAccess, IBlock_TagMemoryAccess_Response
import RL866.state
from RL866.tag_memory_access_command import TagMemoryAccessCommand

log = logging.getLogger(__name__)

def bic(bin: str):
  return chr(int(str(bin),2))

def hic(hex: str):
  return chr(int(str(hex),16))

def iic(i: int):
  return chr(i)

def bi(bin: str):
  return chr(int(str(bin),2))

def hi(hex: str):
  return chr(int(str(hex),16))

def ii(i: int):
  return chr(i)


def write(ser, msg):
  log.info(f"WRITE--> {type(msg)}")
  data = msg.pack()
  for b in data: print(hex(b), ' ', end='')
  print()
  rv = ser.write(data)
  log.info(f"-->WRITE {type(msg)}")
  return rv

timeout = 5
def read(ser: serial.Serial, msg_class: type):
  log.info(f"READ WAITING--> {msg_class}")
  slept = 0
  while(ser.in_waiting == 0):
    time.sleep(0.1)
    slept += 0.1
    if slept > timeout:
      raise Exception("read timeout")

  rv_a = bytearray()
  while ser.in_waiting:
    log.info(f"READ--> {msg_class}")
    #rv = ser.read(255)
    rv = ser.readline()
    rv_a += rv
    time.sleep(0.1)
  for b in rv_a: print(hex(b), ' ', end='')
  print()
  log.info(f"-->READ {msg_class}")
  return rv_a

ser = serial.Serial()
ser.baudrate = 38400
ser.parity = serial.PARITY_EVEN
ser.port = '/dev/ttyUSB0'
ser.timeout = 0
ser.open()

log.info("\n-------serial-------")
log.info(ser.__dict__)

log.info("\n-------RESYNC-------")
msg = SBlock_RESYNC()
write(ser, msg)
msg = SBlock_RESYNC_Response(read(ser, SBlock_RESYNC_Response))

log.info("\n-------IBlock_ReadSystemConfigurationBlock-------")
msg = IBlock_ReadSystemConfigurationBlock(read_ROM=0, read_blocks=1)
write(ser, msg)
msg = IBlock_ReadSystemConfigurationBlock_Response(read(ser, IBlock_ReadSystemConfigurationBlock_Response))

log.info("\n-------IBlock_ReadSystemConfigurationBlock-------")
msg = IBlock_ReadSystemConfigurationBlock()
write(ser, msg)
msg = IBlock_ReadSystemConfigurationBlock_Response(read(ser, IBlock_ReadSystemConfigurationBlock_Response))

log.info("\n-------IBlock_TagInventory-------")
msg = IBlock_TagInventory()
write(ser, msg)
msg = IBlock_TagInventory_Response(read(ser, IBlock_TagInventory_Response))
tag = msg.tags[0]

log.info("\n-------IBlock_TagConnect-------")
msg = IBlock_TagConnect(tag)
write(ser, msg)
msg = IBlock_TagConnect_Response(read(ser, IBlock_TagConnect_Response), tag)

log.info("\n-------IBlock_TagMemoryAccess-------")
mac = TagMemoryAccessCommand().ISO15693_Reset()
msg = IBlock_TagMemoryAccess(tag, mac)
write(ser, msg)
msg = IBlock_TagMemoryAccess_Response(read(ser, IBlock_TagMemoryAccess_Response), tag, mac)

log.info("\n-------IBlock_TagMemoryAccess-------")
mac = TagMemoryAccessCommand().ISO15693_GetTagSystemInformation()
msg = IBlock_TagMemoryAccess(tag, mac)
write(ser, msg)
msg = IBlock_TagMemoryAccess_Response(read(ser, IBlock_TagMemoryAccess_Response), tag, mac)
log.info(msg.__dict__)
log.info(msg.mac_command.__dict__)
log.info(msg.tag.__dict__)

log.info("\n-------IBlock_TagMemoryAccess-------")
mac = TagMemoryAccessCommand().ISO15693_WriteSingleBlock(block_address=5, block_data=b'\xFF\xDD\x00\xAA') # Writing 5 bytes, only actually writes 4
msg = IBlock_TagMemoryAccess(tag, mac)
write(ser, msg)
msg = IBlock_TagMemoryAccess_Response(read(ser, IBlock_TagMemoryAccess_Response), tag, mac)
log.info(msg.__dict__)
log.info(msg.mac_command.__dict__)
log.info(msg.tag.__dict__)

log.info("\n-------IBlock_TagMemoryAccess-------")
mac = TagMemoryAccessCommand().ISO15693_ReadMultipleBlocks()
msg = IBlock_TagMemoryAccess(tag, mac)
write(ser, msg)
msg = IBlock_TagMemoryAccess_Response(read(ser, IBlock_TagMemoryAccess_Response), tag, mac)
log.info(msg.__dict__)
log.info(msg.mac_command.__dict__)
log.info(msg.tag.__dict__)

log.info("\n-------IBlock_TagDisconnect-------")
msg = IBlock_TagDisconnect(tag)
write(ser, msg)
msg = IBlock_TagDisconnect_Response(read(ser, IBlock_TagDisconnect_Response), tag)
