#!/usr/bin/python3
"""
RFID test bed
"""

import lib.iso15692.iso15692 as iso15692
import lib.iso28560.iso28560 as iso28560

from lainuri.config import c
from lainuri.logging_context import logging
log = logging.getLogger(__name__)

import lainuri.websocket_server
import lainuri.rfid_reader
import lainuri.RL866.iblock as iblock
import lainuri.RL866.state as state
from lainuri.RL866.tag_memory_access_command import TagMemoryAccessCommand

from pprint import pprint

rfid_reader = lainuri.rfid_reader.RFID_Reader()
rfid_reader.do_inventory()

tags = lainuri.rfid_reader.get_current_inventory_status()
if len(tags) != 1: raise Exception(f"Only one tags need to be in the reader! Current tags detected '{len(tags)}'")
tag = tags[0]


print("Connecting to tag")
bytes_written = rfid_reader.write( iblock.IBlock_TagConnect(tag) )
tag_connect_response = iblock.IBlock_TagConnect_Response(rfid_reader.read(''), tag)

print("Read tag system information to determine the gate_security_check_block address")
tag_memory_access_command = TagMemoryAccessCommand().ISO15693_GetTagSystemInformation()
bytes_written = rfid_reader.write(iblock.IBlock_TagMemoryAccess(tag, tag_memory_access_command))
tag_system_information_response = iblock.IBlock_TagMemoryAccess_Response(rfid_reader.read(''), tag, tag_memory_access_command)
tag_system_info = tag_system_information_response.mac_command.response
pprint(tag_system_info)

print("Reading tag memory internals")
tag_memory_access_command = TagMemoryAccessCommand().ISO15693_ReadMultipleBlocks(
  read_security_status=0,
  start_block_address=0,
  number_of_blocks_to_read=256
)
bytes_written = rfid_reader.write(iblock.IBlock_TagMemoryAccess(tag, tag_memory_access_command))
tag_memory_access_response = iblock.IBlock_TagMemoryAccess_Response(rfid_reader.read(''), tag, tag_memory_access_command)
pprint(tag_memory_access_response.mac_command.response)

iso28560_o = iso28560.new_data_object(
  afi=tag_system_info['afi'],
  dsfid=tag_system_info['dsfid'],
  block_size=tag_system_info['block_size'],
  memory_capacity_blocks=tag_system_info['tag_memory_capacity_blocks'],
  tag_memory=tag_memory_access_response.mac_command.response['field2'],
)

pprint(iso28560_o.__dict__)

print("Writing AFI")
security_block = b'\x9E'
tag_memory_access_command = TagMemoryAccessCommand().ISO15693_Write_AFI(    tag=tag,    byte=security_block,  )
bytes_written = rfid_reader.write(iblock.IBlock_TagMemoryAccess(tag, tag_memory_access_command))
set_afi = iblock.IBlock_TagMemoryAccess_Response(rfid_reader.read(''), tag, tag_memory_access_command)

print("Enabling EAS")
tag_memory_access_command = TagMemoryAccessCommand().ISO15693_Enable_EAS(tag=tag)
bytes_written = rfid_reader.write(iblock.IBlock_TagMemoryAccess(tag, tag_memory_access_command))
set_eas = iblock.IBlock_TagMemoryAccess_Response(rfid_reader.read(''), tag, tag_memory_access_command)

print("Check EAS Alarm")
tag_memory_access_command = TagMemoryAccessCommand().ISO15693_EAS_Alarm(tag=tag)
bytes_written = rfid_reader.write(iblock.IBlock_TagMemoryAccess(tag, tag_memory_access_command))
eas_alarm = iblock.IBlock_TagMemoryAccess_Response(rfid_reader.read(''), tag, tag_memory_access_command)

print("Disabling EAS")
tag_memory_access_command = TagMemoryAccessCommand().ISO15693_Enable_EAS(tag=tag)
bytes_written = rfid_reader.write(iblock.IBlock_TagMemoryAccess(tag, tag_memory_access_command))
dis_eas = iblock.IBlock_TagMemoryAccess_Response(rfid_reader.read(''), tag, tag_memory_access_command)


import pdb; pdb.set_trace()


# Write the security block
security_block = b'\x07' if 'not-loaned' else b'\xC2'
tag_memory_access_command = TagMemoryAccessCommand().ISO15693_Write_AFI(
  tag=tag,
  byte=security_block,
)
bytes_written = rfid_reader.write(iblock.IBlock_TagMemoryAccess(tag, tag_memory_access_command))
tag_memory_access_response = iblock.IBlock_TagMemoryAccess_Response(rfid_reader.read(''), tag, tag_memory_access_command)



print("Disconnect the tag from the reader")
bytes_written = rfid_reader.write( iblock.IBlock_TagDisconnect(tag) )
tag_disconnect_response = iblock.IBlock_TagDisconnect_Response(rfid_reader.read(''), tag)
