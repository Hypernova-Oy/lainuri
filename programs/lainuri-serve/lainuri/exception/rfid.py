import lainuri.exception

class GateSecurityStatusVerification(lainuri.exception.RFID):
  """
  Gate security status couldn't be confirmed
  """
  def __init__(self, id: str):
    self.id = id

class RFIDCommand(lainuri.exception.RFID):
  """
  RFID command failed with a response error code or response structure was invalid
  """
  def __init__(self, id: str, description: str):
    self.id = id
    self.description = description

class TagNotDetected(lainuri.exception.RFID):
  """
  The given tag was not found in the RFID reader's reading radius
  """
  def __init__(self, id: str):
    self.id = id

class RFIDReset(lainuri.exception.RFID):
  """
  RFID Reader has failed too many times and is now reseting and rebooting.
  """
  def __init__(self, duration: int):
    self.duration = duration

class RFIDTimeout(lainuri.exception.RFID):
  pass

class TagMalformed(lainuri.exception.RFID):
  """
  The given tag's data model and/or tag specifications are inconsistent with the ISO standards
  """
  def __init__(self, id: str, description: str):
    self.id = id
    self.description = description
