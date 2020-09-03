import lainuri.exception

class ReceiptPrintingRetryFailed(lainuri.exception.Printer):
  """
  Couldn't get the thermal receipt printed no matter what.
  """
  def __init__(self, description: str):
    self.description = description
