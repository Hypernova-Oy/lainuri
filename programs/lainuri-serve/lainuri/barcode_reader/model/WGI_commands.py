from lainuri.config import get_config
from lainuri.logging_context import logging
log = logging.getLogger(__name__)

from functools import reduce


class WGICommand():
  # Shared message portions
  source         = b'\x57' # 0x57  means terminal send to decoder or 0x52  means decoder send to terminal
  checksum       = b'\x00\x00'

  # These must be set from the actual commands
  length         = b''
  exID           = b''
  exCMD          = b''
  data           = b''

  def __init__(self):
    if not self.exID:  raise Exception(f"exID not set for command '{type(self)}'!")
    if not self.exCMD: raise Exception(f"exCMD not set for command '{type(self)}'!")
    if not self.data:  raise Exception(f"data not set for command '{type(self)}'!")

  def pack(self):
    """
    message_format = ['Length', 'Source', 'ExID', 'ExCMD', 'Data', 'Checksum High byte', 'Checksum Low byte']
    """
    #length = 1 + len(self.source) + len(self.exID) + len(self.exCMD) + len(self.data)
    self.length = bytes([1 + len(self.source) + len(self.exID) + len(self.exCMD) + len(self.data)])
    payload = self.length + self.source + self.exID + self.exCMD + self.data
    (checksumHighByte, checksumLowByte) = self.calculate_checksum()
    rv = payload + checksumHighByte + checksumLowByte
    log.debug(f"Length='{self.length.hex()}' Source='{self.source.hex()}' ExID='{self.exID.hex()}' ExCMD='{self.exCMD.hex()}' Data='{self.data.hex()}' ChkHB='{checksumHighByte.hex()}' ChkLB='{checksumLowByte.hex()}'")
    return rv

  def calculate_checksum(self):
    self.checksum = 0x10000 - self.byte_to_int(self.length) - self.byte_to_int(self.source) - self.byte_to_int(self.exID) - self.byte_to_int(self.exCMD) \
          - reduce(lambda a, reducer : a + reducer, self.data, 0)
    return (bytes([(self.checksum & 0xFF00) >> 8]), # High byte
            bytes([(self.checksum & 0x00FF)])) # Low byte

  def byte_to_int(self, by):
      return int.from_bytes(by, byteorder="little")

class WGI_AimingLight(WGICommand):
  """
  ?
  """
  exID  = b'\xA1'
  exCMD = b'\x03'
  def __init__(self, turn_off=None, when_scan=None, always_on=None):
    if when_scan or (not(turn_off) and not(when_scan) and not(always_on)):
      self.data = b'\x01'
    if turn_off:
      self.data = b'\x00'
    else:
      self.data = b'\x02'
    super().__init__()

class WGI_ErrorCheck(WGICommand):
  """
  ?
  """
  exID  = b'\xA1'
  exCMD = b'\x0B'
  def __init__(self, turn_off=None, read_twice=None, read_thrice=None):
    if turn_off:
      self.data = b'\x01'
    if read_twice:
      self.data = b'\x02'
    if read_thrice:
      self.data = b'\x03'
    else:
      raise Exception(f"WGI_ErrorCheck() invoked without defining the proper operational mode!")
    super().__init__()

class WGI_IlluminateWorkMode(WGICommand):
  """
  ?
  """
  exID  = b'\xA1'
  exCMD = b'\x04'
  def __init__(self, turn_off=None, when_scan=None, always_on=None):
    if when_scan or (not(turn_off) and not(when_scan) and not(always_on)):
      self.data = b'\x01'
    if turn_off:
      self.data = b'\x00'
    else:
      self.data = b'\x02'
    super().__init__()

class WGI_ConfirmCommunicationStatus(WGICommand):
  """
  ?
  """
  exID  = b'\x0E'
  exCMD = b'\x0D'
  data  = b'\x01'
  def __init__(self):
    super().__init__()

class WGI_ReadVersion(WGICommand):
  """
  ?
  """
  exID  = b'\x0E'
  exCMD = b'\x0D'
  data  = b'\x02'
  def __init__(self):
    super().__init__()

class WGI_RestoreDefault(WGICommand):
  """
  ?
  """
  exID  = b'\xA1'
  exCMD = b'\x01'
  data  = b'\x0F'
  def __init__(self):
    super().__init__()

class WGI_ScanControl(WGICommand):
  """
  ?
  """
  exID  = b'\xA0'
  exCMD = b'\x01'
  def __init__(self, start_scan=None, stop_scan=None):
    if start_scan or (start_scan == None and stop_scan == None):
      self.data = b'\x01'
    else:
      self.data = b'\x00'
    super().__init__()

class WGI_ScanMode(WGICommand):
  """
  ?
  """
  exID  = b'\xA1'
  exCMD = b'\x02'
  def __init__(self, trigger_scan=None, auto_scan=None, continuous_scan=None):
    if not trigger_scan and not auto_scan and not continuous_scan:
      raise Exception(f"No Scan mode given!")
    if trigger_scan:
      self.data = b'\x01'
    if auto_scan:
      self.data = b'\x02'
    if continuous_scan:
      self.data = b'\x03'
    super().__init__()

class WGI_TurnOnAllCode(WGICommand):
  """
  ?
  """
  exID  = b'\xB0'
  exCMD = b'\x01'
  data =  b'\x0E'
  def __init__(self):
    super().__init__()

class WGI_TurnOn1DCode(WGICommand):
  """
  ?
  """
  exID  = b'\xB0'
  exCMD = b'\x01'
  data =  b'\x01'
  def __init__(self):
    super().__init__()

class WGI_TurnOn2DCode(WGICommand):
  """
  ?
  """
  exID  = b'\xB0'
  exCMD = b'\x01'
  data =  b'\x02'
  def __init__(self):
    super().__init__()

class WGI_ACKFeedback(WGICommand):
  """
  ?
  """
  exID  = b'\xA0'
  exCMD = b'\x00'
  def __init__(self, turn_on=None, turn_off=None):
    if turn_on or (not turn_on and not turn_off):
      self.data = b'\x01'
    else:
      self.data = b'\x00'
    super().__init__()

