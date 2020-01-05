import RL866.CRC16
import RL866.state

class Message():

  """
  SOF = b'\xFA' # Start byte of frame
  LEN = b'\x00' # The length including all data field except SOF
  RID = b'\x00' # Remote node address, value FFh is broadcast address. Can apply to RS485 bus.
  PCB = b'\x00' # Protocol control byte
  INF = None # Information field ,the INF of I-block is APDU data
  CHKSUM = b'\x00\x00' # CRC16 check sum, all data except SOF field.
  data = bytearray([
    0xFA, # SOF - Start byte of frame
    0x00, # LEN - The length including all data field except SOF
    0x00, # RID - Remote node address, value FFh is broadcast address. Can apply to RS485 bus.
    0x00, # PCB - Protocol control byte
    0x00, # INF - Information field ,the INF of I-block is APDU data
    0x00,
    0x00,
    0x0000 # CHKSUM - CRC16 check sum, all data except SOF field.
  ])
  """

  SOF = b'\xFA'
  LEN = b''
  RID = b''
  PCB = b''
  INF = b''
  CHK = b''
  PARM = b''
  STA = b''
  CMD = b''

  def __init__(self, RID=None, PCB=None, INF=None):
    self.RID = RID or b''
    self.PCB = PCB or b''
    self.INF = INF or b''

  def sof(self, SOF=None) -> bytes:
    if SOF:
      if SOF != b'\xFA': raise Exception(f"${type(self)} - invalid SOF '{hex(SOF)}'")
      self.SOF = SOF
    return self.SOF

  def rid(self, RID=None) -> bytes:
    if RID:
      self.RID = RID
    return self.RID

  def pcb(self, PCB=None) -> bytes:
    if PCB:
      self.PCB = PCB
    return self.PCB

  def inf(self, INF=None) -> bytes:
    if INF:
      self.INF = INF
    return self.INF

  def len(self, LEN=None) -> bytes:
    """
    The length including all data field except SOF, the maximum length of the packet is 255,
    if the I-block packet exceed MAX length, need to implement Chaining function.
    """
    length = 1 # Count LEN to the total payload size
    if self.RID: length += 1
    if self.PCB: length += 1
    if self.INF: length += len(self.INF)
    length += 2 if self.CHK else 2
    self.LEN = length.to_bytes(1, byteorder='big')

    if LEN and bytes([length]) != LEN: raise Exception(f"${type(self)} - Given length '{LEN}' is not of the expected length '{length}'")
    return self.LEN

  def pack(self) -> bytes:
    self.len()

    data = self.SOF + self.LEN + self.RID + self.PCB
    if self.INF: data += self.INF

    data += self.chk()
    return data

  def chk(self, CHK=None):
    data = self.LEN + self.RID + self.PCB
    if self.INF: data += self.INF

    self.CHK = RL866.CRC16.crc16(data)

    if CHK and CHK != self.CHK: raise Exception(f"${type(self)} - Given checksum '{CHK}' is not the expected checksum '{self.CHK}'")
    return self.CHK

def parseMessage(self, bs: bytes):
  """
  STATIC function to parse
  """
  self.SOF = bytes([bs[0]])
  self.LEN = bytes([bs[1]])
  self.RID = bytes([bs[2]])
  self.PCB = bytes([bs[3]])
  self.CHK = bs[-2:]
  self.INF = bs[4:-2]

  if not self.CHK == RL866.CRC16.crc16(self.LEN + self.RID + self.PCB + self.INF):
    raise Exception("CRC not matches")

def parseIBlockResponseINF(self):
  if not getattr(self, 'INF', None): raise Exception(f"Trying to parse IBlock INF but the given message '{self}' is missing self.INF")
  if not getattr(self, 'CMD', None): raise Exception(f"Trying to parse IBlock INF but the given message '{self}' is missing self.CMD")

  CMD = bytes([self.INF[0]])
  self.STA = self.INF[1:3] # Extract WORD bytes
  self.PARM = self.INF[3:]

  if not self.CMD == CMD: raise Exception(f"Trying to parse IBlock INF but the given message '{self}' has conflicting CMDs? Class isntance CMD='{self.CMD}'. INF contains CMD='{CMD}'?")

  if self.STA[0] or self.STA[1]:
    # TODO: Not sure about the endianness of the bytes
    #status = (self.STA[0] <<8) + self.STA[1]
    status = (self.STA[1] <<8) + self.STA[0]
    error = RL866.state.error_codes.get(status)
    if not error: raise Exception(f"Given message '{self}' has status error '{hex(status)}' but there is no matching error code?")
    raise Exception(f"Given message '{self}' has status error '{error}'")
