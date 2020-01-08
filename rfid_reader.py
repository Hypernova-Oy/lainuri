#!/usr/bin/python3

import serial
import time

from logging_context import logging
from RL866.message import Message
from RL866.sblock import SBlock_RESYNC, SBlock_RESYNC_Response
from RL866.iblock import IBlock_ReadSystemConfigurationBlock, IBlock_ReadSystemConfigurationBlock_Response, IBlock_TagInventory, IBlock_TagInventory_Response, IBlock_TagConnect, IBlock_TagConnect_Response, IBlock_TagDisconnect, IBlock_TagDisconnect_Response, IBlock_TagMemoryAccess, IBlock_TagMemoryAccess_Response
import RL866.state
from RL866.tag_memory_access_command import TagMemoryAccessCommand

log = logging.getLogger(__name__)


class RFID_reader():

  def __init__(self):
    self.serial = self.connect_serial()

    log.info("Connecting serial():> RESYNC")
    self.write(SBlock_RESYNC())
    SBlock_RESYNC_Response(self.read(SBlock_RESYNC_Response))

  def connect_serial(self) -> serial.Serial:
    log.info("Connecting serial")
    ser = serial.Serial()
    ser.baudrate = 38400
    ser.parity = serial.PARITY_EVEN
    ser.port = '/dev/ttyUSB0'
    ser.timeout = 0
    ser.open()

    return ser

  def write(self, msg: Message):
    log.info(f"WRITE--> {type(msg)}")
    data = msg.pack()
    for b in data: print(hex(b), ' ', end='')
    print()
    rv = self.serial.write(data)
    log.info(f"-->WRITE {type(msg)}")
    return rv

  def read(self, msg_class: type):
    timeout = 5
    log.info(f"READ WAITING--> {msg_class}")
    slept = 0
    while(self.serial.in_waiting == 0):
      time.sleep(0.1)
      slept += 0.1
      if slept > timeout:
        raise Exception("read timeout")

    rv_a = bytearray()
    while self.serial.in_waiting:
      log.info(f"READ--> {msg_class}")
      #rv = ser.read(255)
      rv = self.serial.readline()
      rv_a += rv
      time.sleep(0.1)
    for b in rv_a: print(hex(b), ' ', end='')
    print()
    log.info(f"-->READ {msg_class}")
    return rv_a

rfid_reader = RFID_reader()
