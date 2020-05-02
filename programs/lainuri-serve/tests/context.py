import os
import sys

sys.path.append(
    os.path.join(
        os.path.abspath(os.path.dirname(__file__)),
        '../',
    )
)

import lainuri.config
from lainuri.logging_context import logging


def assert_raises(name, e_class, e_string, cb):
  try:
    cb()
    raise AssertionError(name + " failed to raise! " + cb)
  except Exception as e:
    assert type(e) == e_class
    assert e_string in str(e)
