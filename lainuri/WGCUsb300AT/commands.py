from lainuri.config import get_config
from lainuri.logging_context import logging
log = logging.getLogger(__name__)

class WGCCommand():
  # Shared message portions
  message_source = b'\x04'
  message_target = b'\x31'
  reserve        = b'\x00'
  beeper         = b'\x31' # 0xFF Disable, 0x31 Enable
  checksum       = b''

  # These must be set from the actual commands
  length         = b''
  opcode         = b''
  command        = b''

  def __init__(self):
    if not self.command: raise Exception(f"Comand not set for command '{type(self)}'!")

  def pack(self):
    """
    message_format = ['Length', 'MessageSource', 'MessageTarget', 'Reserve', 'Opcode', 'Command', 'Beeper', 'CheckSum']
    """
    payload = self.length + self.message_source + self.message_target + self.reserve + self.opcode + self.command + self.beeper
    return payload + self.calculate_checksum(payload)

  def calculate_checksum(self, payload: bytes) -> bytes:
    """
    1. Check Sum: Radix complement of command sum, high byte in the beginning and low byte in the end.
    Check digit calculation method:
      Adding up all bytes to get sum before checking (excluding two check digit bytes).
      Check digit value=Sum reversed as per digit then add one.
    Example:
      Save & Exit (0A 04 31 00 24 25 45 4E 44 FF)
      adding up to obtain the sum:
        02 5E
      switch to binary (0000 0010 0101 1110),
      then reverse (1111 1101 1010 0001),
      finally add one is check digit
        FD A2
    """
    sum = 0
    for byte in payload:
      sum += byte
    # Complement the bits, but only pick the first 2 bytes we are interested in.
    # Add +1 per the Radix complement algorithm
    cs = (~sum & 0xFFFF) + 1
    # Now the dirty ugly formatting hack to split the checksum to two bytes.
    cs = bytes([
      cs & 0xFF00 >> 8, # Shift the second byte to right, this pushes the first byte out and leaves only the second byte
      cs & 0x00FF       # Pick the first byte by AND-masking the first 8 bits
    ])
    self.checksum = cs
    return cs


class WGC_SettingsEnter(WGCCommand):
  """
  Enter setting mode
  """
  length = b'\x0A'
  opcode = b'\x24'
  command = b'%SET'
  def __init__(self):
    super().__init__()

class WGC_SettingsExit(WGCCommand):
  """
  Save & Exit
  """
  length = b'\x0A'
  opcode = b'\x24'
  command = b'%END'
  def __init__(self):
    super().__init__()

class WGC_ScanTrigger(WGCCommand):
  """
  Trigger scan
  """
  length = b'\x08'
  opcode = b'\x26'
  command = b'LT'
  def __init__(self):
    super().__init__()

class WGC_ScanStop(WGCCommand):
  """
  Stop scan
  """
  length = b'\x08'
  opcode = b'\x27'
  command = b'LS'
  def __init__(self):
    super().__init__()

class WGC_FactoryDefaults(WGCCommand):
  """
  Restore factory default
  """
  length = b'\x08'
  opcode = b'\x28'
  command = b'DF'
  def __init__(self):
    super().__init__()

class WGC_VersionRead(WGCCommand):
  """
  Read program version
  """
  length = b'\x08'
  opcode = b'\x2B'
  command = b'RV'
  def __init__(self):
    super().__init__()

class WGC_Beep(WGCCommand):
  """
  Maybe beeps?
  """
  length = b'\x0F'
  opcode = b'\x31'
  command = [0x2F, 0x03, 0x05, 0x04, 0x01, 0x04, 0x05, 0x04, 0x0A]
  def __init__(self):
    super().__init__()

class WGC_ACK(WGCCommand):
  """
  Maybe talks back?
  """
  length = b'\x07'
  opcode = b'\x3F'
  command = [0x2F]
  def __init__(self):
    super().__init__()

class WGC_SerialPortRespond(WGCCommand):
  """
  4.3.3 Serial port respond
  """
  length = b'\x0B'
  opcode = b'\x50'
  command = b'E0000'
  def __init__(self, disable_respond=0, enable_respond=None):
    if disable_respond: self.command = b'E0000'
    if enable_respond:  self.command = b'E0001'
    super().__init__()

class WGC_F0001(WGCCommand):
  """
  Continuous read
  """
  length = b'\x0B'
  opcode = b'\x50'
  command = b'F0001'
  def __init__(self):
    super().__init__()

class WGC_F0410(WGCCommand):
  """
  Serial command/infrared self-sensing trigger scan timeout 1000ms
  """
  length = b'\x0B'
  opcode = b'\x50'
  command = b'F0410'
  def __init__(self):
    super().__init__()

class WGC_AllBarcodes(WGCCommand):
  """
  Disable read all barcodes
  """
  length = b'\x0B'
  opcode = b'\x50'
  command = b'I1001'
  def __init__(self, disable_all_barcodes=0, enable_all_barcodes=0):
    if disable_all_barcodes: self.command = b'I1000'
    if enable_all_barcodes: self.command = b'I1001'
    super().__init__()

class WGC_Code39Enable(WGCCommand):
  """
  Code39 Enable
  """
  length = b'\x0B'
  opcode = b'\x50'
  command = b'IF001'
  def __init__(self):
    super().__init__()

class WGC_Code39MinBarcodeLength(WGCCommand):
  """
  Code39 Min barcode length, from 5 to 16
  """
  length = b'\x0B'
  opcode = b'\x50'
  command = b'IF810'
  def __init__(self, min_barcode_length):
    if min_barcode_length < 5:  raise Exception("min_barcode_length must be more than 4!")
    if min_barcode_length > 16: raise Exception("min_barcode_length must be less than 17!")
    as_string = 'IF8' + "%02d" % min_barcode_length
    self.command = bytes(as_string, 'ascii')
    super().__init__()

class WGC_Code39MaxBarcodeLength(WGCCommand):
  """
  Code39 Max barcode length, from 10 to 24
  """
  length = b'\x0B'
  opcode = b'\x50'
  command = b'IF916'
  def __init__(self, max_barcode_length):
    if max_barcode_length < 10:  raise Exception("max_barcode_length must be more than 9!")
    if max_barcode_length > 24: raise Exception("max_barcode_length must be less than 25!")
    as_string = 'IF9' + "%02d" % max_barcode_length
    self.command = bytes(as_string, 'ascii')
    super().__init__()

class WGC_BarcodesSetSuffix(WGCCommand):
  """
  Set barcode suffix for all barcode types
  0x0D or 0x0A or 0x0D + 0x0A
  """
  length = b'\x0B'
  opcode = b'\x50'
  command = b'J2000'
  def __init__(self, disable_suffix=0, carriage_return_suffix=0, newline_suffix=0):
    if disable_suffix: self.command = b'J2000'
    elif carriage_return_suffix and newline_suffix: self.command = b'J2003'
    elif carriage_return_suffix: self.command = b'J2001'
    elif newline_suffix: self.command = b'J2002'
    super().__init__()

class WGC_TTL_RS232(WGCCommand):
  """
  Data output mode - TTL/RS232 -mode
  """
  length = b'\x0B'
  opcode = b'\x50'
  command = b'A0000'
  def __init__(self):
    super().__init__()

class WGC_USB_HID(WGCCommand):
  """
  Data output mode - USB HID Keyboard
  """
  length = b'\x0B'
  opcode = b'\x50'
  command = b'A0001'
  def __init__(self):
    super().__init__()

class WGC_USB_COM(WGCCommand):
  """
  Data output mode - USB virtual com port
  """
  length = b'\x0B'
  opcode = b'\x50'
  command = b'A0002'
  def __init__(self):
    super().__init__()
