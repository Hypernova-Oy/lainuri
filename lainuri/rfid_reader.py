from lainuri.config import get_config
from lainuri.logging_context import logging
log = logging.getLogger(__name__)

import serial
import time
import _thread as thread
import json

from lainuri.event import LERFIDTagsLost, LERFIDTagsNew, LERFIDTagsPresent
from lainuri.RL866.message import Message
from lainuri.RL866.sblock import SBlock_RESYNC, SBlock_RESYNC_Response
from lainuri.RL866.iblock import IBlock_ReadSystemConfigurationBlock, IBlock_ReadSystemConfigurationBlock_Response, IBlock_TagInventory, IBlock_TagInventory_Response, IBlock_TagConnect, IBlock_TagConnect_Response, IBlock_TagDisconnect, IBlock_TagDisconnect_Response, IBlock_TagMemoryAccess, IBlock_TagMemoryAccess_Response
from lainuri.RL866.tag import Tag
from lainuri.RL866.tag_memory_access_command import TagMemoryAccessCommand
import lainuri.websocket_server


rfid_readers = []

class RFID_Reader():
  def __init__(self):
    rfid_readers.append(self)
    self.tags_present: Tag = []
    self.tags_lost: Tag = []
    self.tags_new: Tag = []
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

  def start_polling_rfid_tags(self):
    thread.start_new_thread(self._rfid_poll, ())

  def _rfid_poll(self):
    log.info("RFID polling starting")
    self

    while(1):
      self.write(IBlock_TagInventory())
      resp = IBlock_TagInventory_Response(self.read(IBlock_TagInventory_Response))

      for new_tag in resp.tags:

        new_tag_already_present = 0
        for tag_old in self.tags_present:
          if tag_old.serial_number() == new_tag.serial_number():
            new_tag_already_present = 1
            break
        if not new_tag_already_present:
          self.tags_new.append(new_tag)
          self.tags_present.append(new_tag)

      for tag_old in self.tags_present:
        old_tag_missing = 1
        for new_tag in resp.tags:
          if tag_old.serial_number() == new_tag.serial_number():
            old_tag_missing = 0
            break
        if old_tag_missing:
          self.tags_lost.append(tag_old)

      #tags_present = [tag in tags_present if not filter(lambda tag_lost: tag.serial_number() == tag_lost.serial_number(), tags_lost) ]
      self.tags_present = [tag for tag in self.tags_present if not [tag_lost for tag_lost in self.tags_lost if tag.serial_number() == tag_lost.serial_number()]]

      if self.tags_new:
        lainuri.websocket_server.push_event(LERFIDTagsNew(self.tags_new, self.tags_present))
      if self.tags_lost:
        lainuri.websocket_server.push_event(LERFIDTagsLost(self.tags_lost, self.tags_present))

      time.sleep(120) # TODO: This should be something like 0.1 or maybe even no sleep?
      self.tags_lost = []
      self.tags_new  = []

    log.info(f"Terminating RFID thread")


def get_current_inventory_status():
  global rfid_readers
  tags_present = []
  for reader in rfid_readers:
    tags_present += reader.tags_present
  return tags_present
