from lainuri.config import get_config
from lainuri.logging_context import logging
log = logging.getLogger(__name__)


import json
import serial
import time
import _thread as thread
import traceback

import lainuri.event as le
from lainuri.RL866.message import Message
from lainuri.RL866.sblock import SBlock_RESYNC, SBlock_RESYNC_Response
from lainuri.RL866.iblock import IBlock_ReadSystemConfigurationBlock, IBlock_ReadSystemConfigurationBlock_Response, IBlock_TagInventory, IBlock_TagInventory_Response, IBlock_TagConnect, IBlock_TagConnect_Response, IBlock_TagDisconnect, IBlock_TagDisconnect_Response, IBlock_TagMemoryAccess, IBlock_TagMemoryAccess_Response
from lainuri.RL866.tag import Tag
from lainuri.RL866.tag_memory_access_command import TagMemoryAccessCommand
import lainuri.RL866.state as rfid_state
import lainuri.websocket_server


rfid_readers = []

class RFID_Reader():

  def __init__(self):
    self.lock = thread.allocate_lock()
    rfid_readers.append(self)
    self.tags_present: Tag = []
    self.tags_lost: Tag = []
    self.tags_new: Tag = []
    self.serial = self.connect_serial()

    log.info("Connecting serial():> RESYNC")
    self.write(SBlock_RESYNC())
    SBlock_RESYNC_Response(self.read(SBlock_RESYNC_Response))

  def access_lock(self) -> thread.LockType:
    return self.lock

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
    log.debug(f"WRITE--> {type(msg)}")
    data = msg.pack()
    if log.getEffectiveLevel() == logging.DEBUG:
      for b in data: print(hex(b), ' ', end='')
      print()
    rv = self.serial.write(data)
    log.debug(f"-->WRITE {type(msg)}")
    return rv

  def read(self, msg_class: type):
    timeout = 5
    log.debug(f"READ WAITING--> {msg_class}")
    slept = 0
    while(self.serial.in_waiting == 0):
      time.sleep(0.1)
      slept += 0.1
      if slept > timeout:
        raise Exception("read timeout")

    rv_a = bytearray()
    while self.serial.in_waiting:
      log.debug(f"READ--> {msg_class}")
      #rv = ser.read(255)
      rv = self.serial.readline()
      rv_a += rv
      time.sleep(0.1)
    if log.getEffectiveLevel() == logging.DEBUG:
      for b in rv_a: print(hex(b), ' ', end='')
      print()
    log.debug(f"-->READ {msg_class}")
    return rv_a

  def start_polling_rfid_tags(self, interval: float = None):
    thread.start_new_thread(self._rfid_poll, (interval, interval))

  def _rfid_poll(self, interval: float = None, interval2: float = None):
    if not interval: interval = get_config('devices.rfid-reader.polling_interval')
    log.info("RFID polling starting")

    err_repeated = 0
    while(1):
      try:
        self.do_inventory()
        time.sleep(interval or 60) # TODO: This should be something like 0.1 or maybe even no sleep?
        err_repeated = 0
      except Exception as e:
        log.error("Getting inventory failed: "+traceback.format_exc())
        err_repeated = err_repeated + 1
        if err_repeated > 10:
          log.error("RFID reading loop fails too frequently, killing it. The server must be restarted.")
          raise e

    log.info(f"Terminating RFID thread")

  def do_inventory(self):
    with self.access_lock():
      self.write(IBlock_TagInventory())
      resp = IBlock_TagInventory_Response(self.read(IBlock_TagInventory_Response))

    self.tags_lost = []
    self.tags_new  = []

    for new_tag in resp.tags:

      new_tag_already_present = 0
      for tag_old in self.tags_present:
        if tag_old.serial_number() == new_tag.serial_number():
          new_tag_already_present = 1
          break
      if not new_tag_already_present:
        self.flesh_tag_details(new_tag)
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

    self.tags_present = [tag for tag in self.tags_present if not [tag_lost for tag_lost in self.tags_lost if tag.serial_number() == tag_lost.serial_number()]]

    if self.tags_new:
      lainuri.websocket_server.push_event(le.LERFIDTagsNew(self.tags_new, self.tags_present))
    if self.tags_lost:
      lainuri.websocket_server.push_event(le.LERFIDTagsLost(self.tags_lost, self.tags_present))

  def flesh_tag_details(self, tag: Tag):
    with self.access_lock():
      self.write( IBlock_TagConnect(tag) )
      IBlock_TagConnect_Response(self.read(''), tag)

      tag_memory_access_command = TagMemoryAccessCommand().ISO15693_GetTagSystemInformation()
      self.write(IBlock_TagMemoryAccess(tag, tag_memory_access_command))
      IBlock_TagMemoryAccess_Response(tag, tag_memory_access_command).receive(self.read(''))

      tag_memory_access_command = TagMemoryAccessCommand().ISO15693_ReadMultipleBlocks(
        read_security_status=0,
        start_block_address=0,
        number_of_blocks_to_read=256
      )
      self.write(IBlock_TagMemoryAccess(tag, tag_memory_access_command))
      IBlock_TagMemoryAccess_Response(tag, tag_memory_access_command).receive(self.read(''))

      self.write( IBlock_TagDisconnect(tag) )
      IBlock_TagDisconnect_Response(self.read(''), tag)

      return tag

def get_current_inventory_status():
  global rfid_readers
  tags_present = []
  for reader in rfid_readers:
    tags_present += reader.tags_present
  return tags_present


def set_tag_gate_alarm(event, flag_on):
  if event.tag_type == "barcode":
    return 1

  # Get the rfid_reader instance to write with
  rfid_reader = rfid_readers[0]

  with rfid_reader.access_lock():
    # Find the RFID tag instance
    tags = rfid.get_current_inventory_status()
    tag = [t for t in tags if t.serial_number() == event.item_barcode]
    if not tag: raise Exception(f"Couldn't find a tag with serial_number='{event.item_barcode}'!")
    if len(tag) > 1: raise Exception(f"Too many tags match serial_number='{event.item_barcode}'!")
    tag = tag[0]

    afi = get_config('devices.rfid-reader.afi-checkout') # just checking if AFI is enabled in general
    if afi: _set_tag_gate_alarm_afi(rfid_reader, tag, flag_on)
    eas = get_config('devices.rfid-reader.eas')
    if eas: _set_tag_gate_alarm_eas(rfid_reader, tag, flag_on)

  return 1

def _set_tag_gate_alarm_direct_memory_access(rfid_reader, tag, flag_on):
  # Connect to the tag
  bytes_written = rfid_reader.write( IBlock_TagConnect(tag) )
  tag_connect_response = IBlock_TagConnect_Response(rfid_reader.read(''), tag)

  # Read tag system information to determine the gate_security_check_block address
  tag_memory_access_command = TagMemoryAccessCommand().ISO15693_GetTagSystemInformation()
  bytes_written = rfid_reader.write(IBlock_TagMemoryAccess(tag, tag_memory_access_command))
  tag_memory_access_response = IBlock_TagMemoryAccess_Response(tag, tag_memory_access_command).receive(rfid_reader.read(''))

  # Calculate the memory address of the gate security block for this tag type
  block_address_of_rfid_security_gate_check = rfid_state.get_gate_security_block_address(tag)

  # Write the security block
  security_block = b'\x36\x37\x38' if flag_on else b'\x00\x00\x00'
  tag_memory_access_command = TagMemoryAccessCommand().ISO15693_WriteMultipleBlocks(
    tag=tag,
    start_block_address=block_address_of_rfid_security_gate_check,
    number_of_blocks_to_write=1,
    blocks_data_bytes=security_block,
  )
  bytes_written = rfid_reader.write(IBlock_TagMemoryAccess(tag, tag_memory_access_command))
  tag_memory_access_response = IBlock_TagMemoryAccess_Response(tag, tag_memory_access_command).receive(rfid_reader.read(''))

  # Confirm the security block has been written
  tag_memory_access_command = TagMemoryAccessCommand().ISO15693_ReadMultipleBlocks(
    read_security_status=0,
    start_block_address=block_address_of_rfid_security_gate_check,
    number_of_blocks_to_read=1
  )
  bytes_written = rfid_reader.write(IBlock_TagMemoryAccess(tag, tag_memory_access_command))
  tag_memory_access_response = IBlock_TagMemoryAccess_Response(tag, tag_memory_access_command).receive(rfid_reader.read(''))

  # Disconnect the tag from the reader, so others may connect
  bytes_written = rfid_reader.write( IBlock_TagDisconnect(tag) )
  tag_disconnect_response = IBlock_TagDisconnect_Response(rfid_reader.read(''), tag)

  if tag_memory_access_response.mac_command.response['data_of_blocks_read'] != security_block:
    raise Exception(f"Writing the gate security status failed! Write was not confirmed.")

def _set_tag_gate_alarm_afi(rfid_reader, tag, flag_on):
  # Connect to the tag
  bytes_written = rfid_reader.write( IBlock_TagConnect(tag) )
  tag_connect_response = IBlock_TagConnect_Response(rfid_reader.read(''), tag)

  # Write the security block
  security_block = bytes([get_config('devices.rfid-reader.afi-checkin')]) if flag_on else bytes([get_config('devices.rfid-reader.afi-checkout')])
  tag_memory_access_command = TagMemoryAccessCommand().ISO15693_Write_AFI(
    tag=tag,
    byte=security_block,
  )
  bytes_written = rfid_reader.write(IBlock_TagMemoryAccess(tag, tag_memory_access_command))
  tag_memory_access_response = IBlock_TagMemoryAccess_Response(tag, tag_memory_access_command).receive(rfid_reader.read(''))

  # Confirm the security block has been written
  tag_memory_access_command = TagMemoryAccessCommand().ISO15693_GetTagSystemInformation()
  bytes_written = rfid_reader.write(IBlock_TagMemoryAccess(tag, tag_memory_access_command))
  tag_system_information_response = IBlock_TagMemoryAccess_Response(tag, tag_memory_access_command).receive(rfid_reader.read(''))
  tag_system_info = tag_system_information_response.mac_command.response

  # Disconnect the tag from the reader, so others may connect
  bytes_written = rfid_reader.write( IBlock_TagDisconnect(tag) )
  tag_disconnect_response = IBlock_TagDisconnect_Response(rfid_reader.read(''), tag)

  if tag_system_info['afi'] != security_block[0]:
    raise Exception(f"Setting the AFI to '{security_block.hex()}'. Current value '{hex(tag_system_info['afi'])}'")

def _set_tag_gate_alarm_eas(rfid_reader, tag, flag_on):
  # Connect to the tag
  bytes_written = rfid_reader.write( IBlock_TagConnect(tag) )
  tag_connect_response = IBlock_TagConnect_Response(rfid_reader.read(''), tag)

  if flag_on:
    # Write the security block
    tag_memory_access_command = TagMemoryAccessCommand().ISO15693_Enable_EAS(tag=tag)
    bytes_written = rfid_reader.write(IBlock_TagMemoryAccess(tag, tag_memory_access_command))
    tag_memory_access_response = IBlock_TagMemoryAccess_Response(tag, tag_memory_access_command).receive(rfid_reader.read(''))

    # Confirm the security block has been written
    ## TODO: EAS_Alarm doesnt work?
    tag_memory_access_command = TagMemoryAccessCommand().ISO15693_EAS_Alarm(tag=tag)
    bytes_written = rfid_reader.write(IBlock_TagMemoryAccess(tag, tag_memory_access_command))
    eas_alarm = IBlock_TagMemoryAccess_Response(tag, tag_memory_access_command).receive(rfid_reader.read(''))
    ## TODO: eas_alarm.mac_command.response.alarm == 1

  else:
    # Write the security block
    tag_memory_access_command = TagMemoryAccessCommand().ISO15693_Disable_EAS(tag=tag)
    bytes_written = rfid_reader.write(IBlock_TagMemoryAccess(tag, tag_memory_access_command))
    tag_memory_access_response = IBlock_TagMemoryAccess_Response(tag, tag_memory_access_command).receive(rfid_reader.read(''))

    # Confirm the security block has been written
    ## TODO: EAS_Alarm doesnt work?
    tag_memory_access_command = TagMemoryAccessCommand().ISO15693_EAS_Alarm(tag=tag)
    bytes_written = rfid_reader.write(IBlock_TagMemoryAccess(tag, tag_memory_access_command))
    eas_alarm = IBlock_TagMemoryAccess_Response(tag, tag_memory_access_command).receive(rfid_reader.read(''))
    ## TODO: eas_alarm.mac_command.response.alarm == 0

  # Disconnect the tag from the reader, so others may connect
  bytes_written = rfid_reader.write( IBlock_TagDisconnect(tag) )
  tag_disconnect_response = IBlock_TagDisconnect_Response(rfid_reader.read(''), tag)
