#!/usr/bin/python3

import serial
import time
import _thread as thread
import json

from lainuri.config import get_config
from lainuri.logging_context import logging
from lainuri.event import LEvent
from lainuri.RL866.message import Message
from lainuri.RL866.sblock import SBlock_RESYNC, SBlock_RESYNC_Response
from lainuri.RL866.iblock import IBlock_ReadSystemConfigurationBlock, IBlock_ReadSystemConfigurationBlock_Response, IBlock_TagInventory, IBlock_TagInventory_Response, IBlock_TagConnect, IBlock_TagConnect_Response, IBlock_TagDisconnect, IBlock_TagDisconnect_Response, IBlock_TagMemoryAccess, IBlock_TagMemoryAccess_Response
from lainuri.RL866.tag import Tag
from lainuri.RL866.tag_memory_access_command import TagMemoryAccessCommand
import lainuri.websocket_server

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



tags_present: Tag = []
tags_lost: Tag = []
tags_new: Tag = []
def rfid_poll(*args):
  global tags_present, tags_lost, tags_new

  log.info("RFID polling starting")
  rfid_reader = RFID_reader()

  while(1):
    rfid_reader.write(IBlock_TagInventory())
    resp = IBlock_TagInventory_Response(rfid_reader.read(IBlock_TagInventory_Response))

    for new_tag in resp.tags:

      new_tag_already_present = 0
      for tag_old in tags_present:
        if tag_old.serial_number() == new_tag.serial_number():
          new_tag_already_present = 1
          break
      if not new_tag_already_present:
        tags_new.append(new_tag)
        tags_present.append(new_tag)

    for tag_old in tags_present:
      old_tag_missing = 1
      for new_tag in resp.tags:
        if tag_old.serial_number() == new_tag.serial_number():
          old_tag_missing = 0
          break
      if old_tag_missing:
        tags_lost.append(tag_old)

    #tags_present = [tag in tags_present if not filter(lambda tag_lost: tag.serial_number() == tag_lost.serial_number(), tags_lost) ]
    tags_present = [tag for tag in tags_present if not [tag_lost for tag_lost in tags_lost if tag.serial_number() == tag_lost.serial_number()]]
    tags_present_serial_numbers = [tag.serial_number() for tag in tags_present]

    if tags_new:
      lainuri.websocket_server.push_event(LEvent("rfid-tags-new", {
        'tags_new': [tag.serial_number() for tag in tags_new],
        'tags_present': tags_present_serial_numbers,
      }))
    if tags_lost:
      lainuri.websocket_server.push_event(LEvent("rfid-tags-lost", {
        'tags_lost': [tag.serial_number() for tag in tags_lost],
        'tags_present': tags_present_serial_numbers,
      }))

    time.sleep(120) # TODO: This should be something like 0.1 or maybe even no sleep?
    tags_lost = []
    tags_new  = []

  log.info(f"Terminating RFID thread")
  exit(0)


def get_current_inventory_status():
  global tags_present
  return {
    'tags_present': [tag.serial_number() for tag in tags_present],
  }

def start():
  if get_config('devices.rfid-reader.enabled'):
    thread.start_new_thread(rfid_poll, ())
  else:
    log.info("RFID reader is disabled by config")
