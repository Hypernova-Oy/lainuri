from lainuri.config import get_config
from lainuri.logging_context import logging
log = logging.getLogger(__name__)


import json
import serial
import time
import _thread as thread
import traceback

from lainuri.constants import Status
import lainuri.event as le
import lainuri.event_queue
import lainuri.exception.rfid as exception_rfid
from lainuri.RL866.message import Message
from lainuri.RL866.sblock import SBlock_RESYNC, SBlock_RESYNC_Response
from lainuri.RL866.iblock import IBlock_ReadSystemConfigurationBlock, IBlock_ReadSystemConfigurationBlock_Response, IBlock_TagInventory, IBlock_TagInventory_Response, IBlock_TagConnect, IBlock_TagConnect_Response, IBlock_TagDisconnect, IBlock_TagDisconnect_Response, IBlock_TagMemoryAccess, IBlock_TagMemoryAccess_Response
from lainuri.RL866.tag import Tag
from lainuri.RL866.tag_memory_access_command import TagMemoryAccessCommand
import lainuri.RL866.state as rfid_state
import lainuri.status
from lainuri.threadbase import Threadbase


rfid_readers = []

def get_rfid_reader():
  if len(rfid_readers) > 0:
    return rfid_readers[0]
  else:
    rfid_readers.append(RFID_Reader())
  return rfid_readers[0]

class RFID_Reader():

  def __init__(self):
    self.lock = thread.allocate_lock()
    self.tags_present: Tag = []
    self.tags_lost: Tag = []
    self.tags_new: Tag = []

    self.reconnect()
    self.reset()

    self.inventory_polling_interval = get_config('devices.rfid-reader.polling_interval')
    self.err_repeated = 0

  def reconnect(self):
    log.info('reconnect():>')
    if getattr(self, 'serial', None): self.serial.close()
    self.serial = self.connect_serial()

  def reset(self):
    log.info("reset():>")
    self.write(SBlock_RESYNC())
    SBlock_RESYNC_Response(self.read(SBlock_RESYNC_Response))

  def access_lock(self) -> thread.LockType:
    return self.lock

  def connect_serial(self) -> serial.Serial:
    log.info("Connecting serial")
    ser = serial.Serial()
    ser.baudrate = 38400
    ser.parity = serial.PARITY_EVEN
    ser.port = '/dev/ttyRL866'
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
        raise exception_rfid.RFIDTimeout(f"read timeout for message class '{msg_class}'")

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

  def start_polling_rfid_tags(self):
    self.daemon = Threadbase(name='RFID-Reader', worker_method=self.rfid_poll_daemon, listen_for_event=False)
    self.daemon.start()
    return self.daemon

  def stop_polling_rfid_tags(self):
    self.daemon.kill()
    return self.daemon

  def rfid_poll_daemon(self):
    try:
      self.do_inventory()
      time.sleep(self.inventory_polling_interval or 1) # TODO: This should be something like 0.1 or maybe even no sleep?

      self.err_repeated = 0
      lainuri.status.update_status('rfid_reader_status', Status.SUCCESS)
    except Exception as e:
      self.err_repeated = self.err_repeated + 1
      log.exception(f"RFID Reader - Getting inventory failed. Sleeping for {self.err_repeated * 2}s and resetting connection.")
      lainuri.status.update_status('rfid_reader_status', Status.ERROR)
      time.sleep(self.err_repeated * 2)

      if type(e) == exception_rfid.RFIDTimeout:
        self.reconnect()
      self.reset()

  def do_inventory(self, no_events: bool = False):
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

    if not no_events:
      if self.tags_new:
        lainuri.event_queue.push_event(le.LERFIDTagsNew(self.tags_new, self.tags_present))
      if self.tags_lost:
        lainuri.event_queue.push_event(le.LERFIDTagsLost(self.tags_lost, self.tags_present))

      # RFIDTagsNew/Lost-events are fast, and show to the GUI that Items are detected. Schedule ItemBib full data load event after showing to the user the RFID tag detection changes.
      if self.tags_new:
        lainuri.event_queue.push_event(le.LEItemBibFullDataRequest([tag.iso25680_get_primary_item_identifier() for tag in self.tags_new]))

    return self

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


def set_tag_gate_alarm(item_barcode: str, flag_on: bool):
  """
  @throws exception.rfid.TagNotDetected
          exception.rfid.RFIDCommand
  """
  # Get the rfid_reader instance to write with
  rfid_reader = rfid_readers[0]

  with rfid_reader.access_lock():
    tag = None

    for try_count in [1,2,3]:
      try:
        # Find the RFID tag instance
        tags = get_current_inventory_status()
        tags = [t for t in tags if t.iso25680_get_primary_item_identifier() == item_barcode]
        if not tags: raise exception_rfid.TagNotDetected(item_barcode)
        tag = tags[0]

        afi = get_config('devices.rfid-reader.afi-checkout') # just checking if AFI is enabled in general
        if afi: _set_tag_gate_alarm_afi(rfid_reader, tag, flag_on)
        eas = get_config('devices.rfid-reader.eas')
        if eas: _set_tag_gate_alarm_eas(rfid_reader, tag, flag_on)

        return tag # Break away from the retry-loop

      except Exception as e:
        log.exception(f"Exception {type(e)}")
        if type(e) == exception_rfid.RFIDCommand:
          _handle_retriable_exception(e, try_count, rfid_reader, tag)
        elif type(e) == exception_rfid.GateSecurityStatusVerification:
          _handle_retriable_exception(e, try_count, rfid_reader, tag)
        else:
          if tag: _finally_tag_disconnect(rfid_reader, tag)
          raise e
  return None

def _finally_tag_disconnect(rfid_reader: RFID_Reader, tag: Tag) -> Tag:
  """
  @returns Tag on success, None on failure
  """
  try:
    # Disconnect the tag from the reader, so others may connect
    rfid_reader.write( IBlock_TagDisconnect(tag) )
    IBlock_TagDisconnect_Response(rfid_reader.read(''), tag)
    return tag
  except Exception as e:
    log.exception(f"Finally disconnecting failed '{tag}':>")
    return None

def _handle_retriable_exception(e: Exception, try_count: int, rfid_reader, tag: Tag):
  if try_count < 3:
    log.warn(f"Retrying '{try_count}'. {str(e)}")
  else:
    log.warn(f"Retries over '{try_count}'. Raising {str(e)}")
    if tag.get_connection_handle():
      if tag: _finally_tag_disconnect(rfid_reader, tag)
    raise e

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
  if get_config('devices.rfid-reader.double-check-gate-security'):
    tag_memory_access_command = TagMemoryAccessCommand().ISO15693_ReadMultipleBlocks(
      read_security_status=0,
      start_block_address=block_address_of_rfid_security_gate_check,
      number_of_blocks_to_read=1
    )
    bytes_written = rfid_reader.write(IBlock_TagMemoryAccess(tag, tag_memory_access_command))
    tag_memory_access_response = IBlock_TagMemoryAccess_Response(tag, tag_memory_access_command).receive(rfid_reader.read(''))

    if tag_memory_access_response.mac_command.response['data_of_blocks_read'] != security_block:
      raise exception_rfid.GateSecurityStatusVerification(tag.iso25680_get_primary_item_identifier())

  # Disconnect the tag from the reader, so others may connect
  bytes_written = rfid_reader.write( IBlock_TagDisconnect(tag) )
  tag_disconnect_response = IBlock_TagDisconnect_Response(rfid_reader.read(''), tag)

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
  if get_config('devices.rfid-reader.double-check-gate-security'):
    tag_memory_access_command = TagMemoryAccessCommand().ISO15693_GetTagSystemInformation()
    bytes_written = rfid_reader.write(IBlock_TagMemoryAccess(tag, tag_memory_access_command))
    tag_system_information_response = IBlock_TagMemoryAccess_Response(tag, tag_memory_access_command).receive(rfid_reader.read(''))
    tag_system_info = tag_system_information_response.mac_command.response

    if tag_system_info['afi'] != security_block[0]:
      raise exception_rfid.GateSecurityStatusVerification(tag.iso25680_get_primary_item_identifier())

  # Disconnect the tag from the reader, so others may connect
  bytes_written = rfid_reader.write( IBlock_TagDisconnect(tag) )
  tag_disconnect_response = IBlock_TagDisconnect_Response(rfid_reader.read(''), tag)

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
    #if get_config('devices.rfid-reader.double-check-gate-security'):
    #tag_memory_access_command = TagMemoryAccessCommand().ISO15693_EAS_Alarm(tag=tag)
    #bytes_written = rfid_reader.write(IBlock_TagMemoryAccess(tag, tag_memory_access_command))
    #eas_alarm = IBlock_TagMemoryAccess_Response(tag, tag_memory_access_command).receive(rfid_reader.read(''))
    ## TODO: eas_alarm.mac_command.response.alarm == 1

  else:
    # Write the security block
    tag_memory_access_command = TagMemoryAccessCommand().ISO15693_Disable_EAS(tag=tag)
    bytes_written = rfid_reader.write(IBlock_TagMemoryAccess(tag, tag_memory_access_command))
    tag_memory_access_response = IBlock_TagMemoryAccess_Response(tag, tag_memory_access_command).receive(rfid_reader.read(''))

    # Confirm the security block has been written
    ## TODO: EAS_Alarm doesnt work?
    #if get_config('devices.rfid-reader.double-check-gate-security'):
    #tag_memory_access_command = TagMemoryAccessCommand().ISO15693_EAS_Alarm(tag=tag)
    #bytes_written = rfid_reader.write(IBlock_TagMemoryAccess(tag, tag_memory_access_command))
    #eas_alarm = IBlock_TagMemoryAccess_Response(tag, tag_memory_access_command).receive(rfid_reader.read(''))
    ## TODO: eas_alarm.mac_command.response.alarm == 0

  # Disconnect the tag from the reader, so others may connect
  bytes_written = rfid_reader.write( IBlock_TagDisconnect(tag) )
  tag_disconnect_response = IBlock_TagDisconnect_Response(rfid_reader.read(''), tag)
