from logging_context import logging
log = logging.getLogger(__name__)
from simple_websocket_server import WebSocketServer, WebSocket
import _thread as thread
import time
import json

from rfid_reader import rfid_reader



clients = []

from RL866.iblock import IBlock_ReadSystemConfigurationBlock, IBlock_ReadSystemConfigurationBlock_Response, IBlock_TagInventory, IBlock_TagInventory_Response, IBlock_TagConnect, IBlock_TagConnect_Response, IBlock_TagDisconnect, IBlock_TagDisconnect_Response, IBlock_TagMemoryAccess, IBlock_TagMemoryAccess_Response
from RL866.tag import Tag
tags_present: Tag = []
tags_lost: Tag = []
tags_new: Tag = []
def rfid_poll(*args):
  global tags_present, tags_lost, tags_new

  log.info("RFID polling starting")

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

    for new_tag in tags_new:
      log.info(f"NEW TAG '{new_tag.serial_number()}'")
      for client in clients:
        log.info("NEW TAG message to client")
        client.send_message("NEW TAG" + new_tag.serial_number())
    for lost_tag in tags_lost:
      log.info(f"LOST TAG '{lost_tag.serial_number()}'")
      for client in clients:
        log.info("LOST TAG message to client")
        client.send_message("LOST TAG" + lost_tag.serial_number())
    for tag in tags_present:
      log.info(f"PRESENT TAG '{tag.serial_number()}'")

    time.sleep(2)
    tags_lost = []
    tags_new  = []

thread.start_new_thread(rfid_poll, ())


def send_current_inventory_status(client: WebSocket):
  global tags_present
  client.send_message("TAGS PRESENT:" + json.dumps([tag.serial_number() for tag in tags_present]))



class SimpleChat(WebSocket):
  def handle(self):
    try:
      global clients
      log.info(f"MESSAGE Received message '{self.__dict__}'")
      for client in clients:
        log.info("Send message to client")
        client.send_message(self.address[0] + u' - ' + self.data)
    except Exception as e:
      log.exception(e)
      raise e

  def connected(self):
    try:
      global clients
      log.info(f"JOINED Hey all, client '{self.__dict__}' just JOINED us!")
      for client in clients:
        client.send_message(self.address[0] + u' - connected')
      clients.append(self)
      send_current_inventory_status(self)
    except Exception as e:
      log.exception(e)
      raise e

  def handle_close(self):
    try:
      global clients
      log.info(f"LEFT Hey all, client '{self.__dict__}' just LEFT us!")
      clients.remove(self)
      for client in clients:
        client.send_message(self.address[0] + u' - disconnected')
    except Exception as e:
      log.exception(e)
      raise e



server = WebSocketServer('localhost', 12345, SimpleChat)
server.serve_forever()
