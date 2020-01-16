from lainuri.config import get_config
from lainuri.logging_context import logging
log = logging.getLogger(__name__)

import traceback

#from lainuri.event import LEvent # Cannot import this even for type safety, due to circular dependency

from lainuri.koha_api import koha_api
import lainuri.websocket_server
import lainuri.event
import lainuri.rfid_reader as rfid
import lainuri.RL866.iblock as iblock
import lainuri.RL866.state as rfid_state
from lainuri.RL866.tag_memory_access_command import TagMemoryAccessCommand

def checkout(event):
  # Checkout to Koha
  statuses = koha_api.checkout(event.barcode, event.borrowernumber)
  if statuses['status'] == 'failed':
    lainuri.websocket_server.push_event(
      lainuri.event.LECheckOutFailed(event.barcode, event.borrowernumber, statuses)
    )
    return

  try:
    set_tag_gate_alarm_off(event)
    # Send a notification to the UI
    lainuri.websocket_server.push_event(
      lainuri.event.LECheckOuted(event.barcode, event.borrowernumber, statuses)
    )
  except Exception:
    statuses['status'] = 'failed'
    statuses['write_to_tag_failed'] = traceback.format_exc()
    lainuri.websocket_server.push_event(
      lainuri.event.LECheckOutFailed(event.barcode, event.borrowernumber, statuses)
    )

def set_tag_gate_alarm_off(event):
  # Get the rfid_reader instance to write with
  rfid_reader = rfid.rfid_readers[0]

  with rfid_reader.access_lock():
    # Find the RFID tag instance
    tags = rfid.get_current_inventory_status()
    tag = [t for t in tags if t.serial_number() == event.barcode]
    if not tag: raise Exception(f"Couldn't find a tag with serial_number='{event.barcode}'!")
    if len(tag) > 1: raise Exception(f"Too many tags match serial_number='{event.barcode}'!")
    tag = tag[0]

    # Connect to the tag
    bytes_written = rfid_reader.write( iblock.IBlock_TagConnect(tag) )
    tag_connect_response = iblock.IBlock_TagConnect_Response(rfid_reader.read(''), tag)

    # Read tag system information to determine the gate_security_check_block address
    tag_memory_access_command = TagMemoryAccessCommand().ISO15693_GetTagSystemInformation()
    bytes_written = rfid_reader.write(iblock.IBlock_TagMemoryAccess(tag, tag_memory_access_command))
    tag_memory_access_response = iblock.IBlock_TagMemoryAccess_Response(rfid_reader.read(''), tag, tag_memory_access_command)

    # Calculate the memory address of the gate security block for this tag type
    block_address_of_rfid_security_gate_check = rfid_state.get_gate_security_block_address(tag)

    # Write the security block
    security_block = b'\x36\x37\x38'
    tag_memory_access_command = TagMemoryAccessCommand().ISO15693_WriteMultipleBlocks(
      tag=tag,
      start_block_address=block_address_of_rfid_security_gate_check,
      number_of_blocks_to_write=1,
      blocks_data_bytes=security_block,
    )
    bytes_written = rfid_reader.write(iblock.IBlock_TagMemoryAccess(tag, tag_memory_access_command))
    tag_memory_access_response = iblock.IBlock_TagMemoryAccess_Response(rfid_reader.read(''), tag, tag_memory_access_command)

    # Confirm the security block has been written
    tag_memory_access_command = TagMemoryAccessCommand().ISO15693_ReadMultipleBlocks(
      read_security_status=0,
      start_block_address=block_address_of_rfid_security_gate_check,
      number_of_blocks_to_read=1
    )
    bytes_written = rfid_reader.write(iblock.IBlock_TagMemoryAccess(tag, tag_memory_access_command))
    tag_memory_access_response = iblock.IBlock_TagMemoryAccess_Response(rfid_reader.read(''), tag, tag_memory_access_command)
    if tag_memory_access_response.mac_command.data_of_blocks_read != security_block:
      raise Exception(f"Writing the gate security status failed! Write was not confirmed.")

    # Disconnect the tag from the reader, so others may connect
    bytes_written = rfid_reader.write( iblock.IBlock_TagDisconnect(tag) )
    tag_disconnect_response = iblock.IBlock_TagDisconnect_Response(rfid_reader.read(''), tag)

  return 1
