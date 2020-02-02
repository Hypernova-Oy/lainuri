class InvalidPassword(Exception):
  pass

class InvalidUser(Exception):
  def __init__(self, id: str):
    self.id = id

class NoResults(Exception):
  pass
