import lainuri.exception

class InvalidUser(lainuri.exception.ILS):
  def __init__(self, id: str):
    self.id = id

class NoUser(lainuri.exception.ILS):
  def __init__(self, id: str):
    self.id = id

class NoItem(lainuri.exception.ILS):
  def __init__(self, id: str):
    self.id = id
