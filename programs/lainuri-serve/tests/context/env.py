"""
Class temporarily Mocks environment variables used within a with-statement
"""

import os

class MockEnv():
  def __init__(self, **kwargs):
    self.old_env = {}
    self.new_env = kwargs

  def __enter__(self):
    for key, value in self.new_env.items():
      self.old_env[key] = os.environ.get(key)
      os.environ.update({key: value})

  def __exit__(self, *args):
    for key, value in self.old_env.items():
      os.environ.update({key: value})
