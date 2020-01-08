from logging_context import logging
log = logging.getLogger(__name__)

import helpers


transmission_sequence_number = 0
def increment_transmission_sequence_number():
  global transmission_sequence_number
  transmission_sequence_number ^= 1
  log.info(f"incremented to '{transmission_sequence_number}'")

RID_request = b'\xFF'

AIR_PROTO_ISO15693 = 1
AIR_PROTO_ISO14443A = 2
AIR_PROTO_ISO14443B = 3
AIR_PROTO_RFID_APL_I18000P3M3_ID = 6
AIR_PROTO_RFID_APL_ICODESLI_ID = 12
TAG_NXP_ICODE_SLI = 1
TAG_TI_HFI_PLUS = 2
TAG_ST_M24LRXX = 3
TAG_FUJ_MB89R118C = 4
TAG_NXP_ICODE_SLIX = 7
TAG_TI_HFI_STANDARD = 8
TAG_TI_HFI_PRO = 9
TAG_NXP_ICODE_SLIX2 = 10
TAG_CIT83128 = 11
TAG_NXP_ICODE_SLIX_S = 12
TAG_Mifare_Ultralight = 1
TAG_MIFARE_S50 = 2
TAG_MIFARE_S70 = 3
TAG_DESFIRE_EV1 = 4
TAG_NTAG21X = 5

air_protocol_type_table = helpers._two_way_link_dict({
  0: 'Unknown',
  1: 'ISO15693',               # supported
  2: 'ISO14443A',              # supported
  3: 'ISO14443B',              # supported
  4: 'Reserved',
  5: 'Reserved',
  6: 'RFID_APL_I18000P3M3_ID', # supported
  7: 'Reserved',
  8: 'Reserved',
  9: 'Reserved',
  10: 'Reserved',
  11: 'Reserved',
  12: 'RFID_APL_ICODESLI_ID',  # supported
})

#Appendix A.Supported tag types
supported_tag_types = {
  #1.ISO15693 tag types:
  AIR_PROTO_ISO15693: helpers._two_way_link_dict({
    1:  'NXP ICODE SLI',
    2:  'TI HFI PLUS',
    3:  'ST M24LRXX',
    4:  'FUJ MB89R118C',
    7:  'NXP ICODE SLIX',
    8:  'TI HFI STANDARD',
    9:  'TI HFI PRO',
    10: 'NXP ICODE SLIX2',
    11: 'CIT83128',
    12: 'NXP ICODE SLIX-S',
  }),

  #2.ISO14443a tag types:
  AIR_PROTO_ISO14443A: helpers._two_way_link_dict({
    1: 'Mifare Ultralight',
    2: 'MIFARE S50',
    3: 'MIFARE S70',
    4: 'DESFIRE/Desfire EV1',
    5: 'NTAG21X',
  })
}

def getAirProtocolCode(air_protocol_inventory_parameters) -> int:
  if isinstance(air_protocol_inventory_parameters.air_interface_protocol, int):
    return air_protocol_inventory_parameters.air_interface_protocol
  else:
    return air_protocol_type_table[ air_protocol_inventory_parameters.air_interface_protocol ]


error_codes = {
#Appendix C.Error Code
#General error:
    0x000: ['ERR_OK', 'OK'],
    0x001: ['ERR_UNKNOWN', 'Unknown error'],
    0x002: ['ERR_ARG', 'Invalid argument'],
    0x003: ['ERR_NOSYS', 'No supported'],
    0x004: ['ERR_TIMEOUT', 'Timeout'],
    0x005: ['ERR_MEM', 'Memory request failed'],
    0x006: ['ERR_NOTSUP', 'Function have not set up'],
    0x007: ['ERR_OVERFLOW', 'Overflow'],
    0x009: ['ERR_IO', 'SPI communication error'],
    0x00A: ['ERR_NEEDRANDOM', 'Need to get random first'],
    0x00B: ['ERR_ARGSIZE', 'Invalid length of parameter'],
    #Message error:
    0x100: ['ERR_MSG_SAD', 'Invalid Message node address'],
    0x101: ['ERR_MSG_CHKSUM', 'Invalid message checksum'],
    0x102: ['ERR_MSG_SIZE', 'Invalid message length'],
    0x103: ['ERR_MSG_OPERCODE', 'Invalid message command'],
    0x104: ['ERR_MSG_SN', 'Invalid message synchronization code'],
    0x105: ['ERR_MSG_PARAM', 'Invalid message parameter'],
    0x106: ['ERR_MSG_BLKTYPE', 'Invalid block type of message'],
    #General application error:
    0x121: ['ERR_INVALID_CFGn', 'Invalid CFG block address'],
    0x122: ['ERR_INVALID_APL', 'Invalid air protocol type'],
    #RFID application error:
    0x400: ['ERR_RFID_WRONG_DATA', 'Wrong data returned from ASIC'],
    0x401: ['ERR_RFID_TRANSC_WRERR', 'Transceive fail with tag'],
    0x402: ['ERR_RFID_TRANSC_TEMPERR', 'Transceive fail with tag'],
    0x403: ['ERR_RFID_TRANSC_BUFFEROVFL', 'ASIC FIFO overflow'],
    0x404: ['ERR_RFID_TRANSC_COLLERR', 'Tags collision'],
    0x405: ['ERR_RFID_TRANSC_CRCERR', 'Invalid checksum of message from tag'],
    0x406: ['ERR_RFID_TRANSC_PARITYERR', 'Invalid parity of message from tag'],
    0x407: ['ERR_RFID_TRANSC_PROTOCOLERR', 'The received data frame does not conform to the air protocol'],
    0x408: ['ERR_RFID_TRANSC_NODATA', 'No data send to tag'],
    0x409: ['ERR_RFID_TRANSC_MINFRAMEERR', 'No minimum frame received'],
    0x40A: ['ERR_RFID_TRANSC_INTEGERR', 'Transceive fail with tag'],
    0x415: ['ERR_RFID_WRONG_HANDLE', 'Wrong handle'],
    0x416: ['ERR_RFID_AUTH_FAIL', 'Authenticate fail'],
    0x417: ['ERR_RFID_ASIC_DEAD', 'ASIC dead'],
    0x418: ['ERR_RFID_ASIC_E2PROM', 'ASIC E2PROM error'],
    0x419: ['ERR_RFID_TAG_COLL', 'Tags collision'],
    0x41A: ['ERR_RFID_INVALID_ADDR_MODE', 'Invalid ISO15693 address mode.'],
    0x41B: ['ERR_RFID_TAG_BLOCK_LOCKED_OR_INVALID_ADDR', 'Data block is locked or invalid data block address'],
    0x41C: ['ERR_RFID_TAG_INVALID_BLK_ADDR', 'Invalid block address'],
    0x41D: ['ERR_RFID_TAG_NO_AUTHORIZE_OR_PWD_LOCKED', 'Unauthenticated or password has been locked'],
    0x41E: ['ERR_RFID_TAG_NO_AUTHORIZE', 'Unauthenticated'],
    0x41F: ['ERR_RFID_TRANSC_RFI', ''],
    0x420: ['ERR_RFID_TAG_NOFOUND', 'No tags found'],
    0x421: ['ERR_RFID_TAG_UNKNOWN', 'Unknown tag type'],
    0x422: ['ERR_RFID_TAG_NAK', 'The tag returns NAK'],
    0x423: ['ERR_RFID_TAG_WRONG_DATA', 'The tag returned incorrect data'],
    0x424: ['ERR_RFID_TAG_WRONG_UID', 'The tag returned an incorrect UID'],
}
