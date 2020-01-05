#!/usr/bin/python3

import serial
import time
from RL866.sblock import SBlock_RESYNC, SBlock_RESYNC_Response
from RL866.iblock import IBlock_ReadSystemConfigurationBlock, IBlock_TagInventory, IBlock_TagInventory_Response
import RL866.state



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


def write(ser, data):
  print('WRITE-->')
  for b in data: print(hex(b), ' ', end='')
  rv = ser.write(data)
  print("\n", rv)
  print('-->WRITE')
  return rv

timeout = 5
def read(ser):
  print("READ WAITING-->")
  slept = 0
  while(ser.in_waiting == 0):
    time.sleep(0.1)
    slept += 0.1
    if slept > timeout:
      raise Exception("read timeout")

  print('READ-->')
  #rv = ser.read(255)
  rv = ser.readline()
  for b in rv: print(hex(b), ' ', end='')
  print()
  print('-->READ')
  return rv

msg = SBlock_RESYNC()


ser = serial.Serial()
ser.baudrate = 38400
ser.parity = serial.PARITY_EVEN
ser.port = '/dev/ttyUSB0'
ser.timeout = 0
ser.open()

print(ser.__dict__)

write(ser, msg.pack())

rv = read(ser)
rr = SBlock_RESYNC_Response(rv)

print(rr.__dict__)

msg = IBlock_ReadSystemConfigurationBlock()
write(ser, msg.pack())
rv = read(ser)

msg = IBlock_ReadSystemConfigurationBlock()
write(ser, msg.pack())
rv = read(ser)

msg = IBlock_TagInventory()
write(ser, msg.pack())
rv = read(ser)
IBlock_TagInventory_Response(rv)
