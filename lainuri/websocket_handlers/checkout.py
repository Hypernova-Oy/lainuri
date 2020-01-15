from lainuri.config import get_config
from lainuri.logging_context import logging
log = logging.getLogger(__name__)

#from lainuri.event import LEvent # Cannot import this even for type safety, due to circular dependency

from lainuri.koha_api import koha_api
import lainuri.websocket_server
import lainuri.event
import lainuri.rfid_reader as rfid
import lainuri.RL866.iblock as iblock
from lainuri.RL866.tag_memory_access_command import TagMemoryAccessCommand

def checkout(event):
  # Get the rfid_reader instance to write with
  rfid_reader = rfid.rfid_readers[0]

  # Checkout to Koha
  statuses = koha_api.checkout(event.barcode, event.borrowernumber)
  if statuses['status'] == 'failed':
    lainuri.websocket_server.push_event(
      lainuri.event.LECheckOutFailed(event.barcode, event.borrowernumber, statuses)
    )
    return

  # Find the RFID tag instance
  tags = rfid.get_current_inventory_status()
  tag = [t for t in tags if t.serial_number() == event.barcode]

  # Connect to the tag
  rv_bytes = rfid_reader.write( iblock.IBlock_TagConnect(tag) )
  tag_connect_response = iblock.IBlock_TagConnect_Response(rv_bytes, tag)

  # Read tag system information to determine the gate_security_check_block address
  tag_memory_access_command = TagMemoryAccessCommand().ISO15693_GetTagSystemInformation()
  rv_bytes = rfid_reader.write(iblock.IBlock_TagMemoryAccess(tag, tag_memory_access_command))
  tag_memory_access_response = iblock.IBlock_TagMemoryAccess_Response(rv_bytes, tag, tag_memory_access_command)

  # Calculate the memory address of the gate security block for this tag type
  rfid_security_gate_check_block_number = 4
  block_address_of_rfid_security_gate_check = tag.block_size * rfid_security_gate_check_block_number

  # Write the security block
  tag_memory_access_command = TagMemoryAccessCommand().ISO15693_WriteSingleBlock(
    block_address_of_rfid_security_gate_check,
    b'\x01'
  )
  rv_bytes = rfid_reader.write(iblock.IBlock_TagMemoryAccess(tag, tag_memory_access_command))
  tag_memory_access_response = iblock.IBlock_TagMemoryAccess_Response(rv_bytes, tag, tag_memory_access_command)

  # Disconnect the tag from the reader, so others may connect
  rv_bytes = rfid_reader.write( iblock.IBlock_TagDisconnect(tag) )
  tag_disconnect_response = iblock.IBlock_TagDisconnect_Response(rv_bytes, tag)

  # Send a notification to the UI
  lainuri.websocket_server.push_event(
    lainuri.event.LECheckOuted(event.barcode, event.borrowernumber, statuses)
  )
