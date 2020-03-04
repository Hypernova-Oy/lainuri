import lainuri.exception

class RFIDCommand(lainuri.exception.RFID):
  """
  RFID command failed with a response error code
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

class GateSecurityStatusVerification(lainuri.exception.RFID):
  """
  Gate security status couldn't be confirmed
  """
  def __init__(self, id: str):
    self.id = id
