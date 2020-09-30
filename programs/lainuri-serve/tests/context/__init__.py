from bs4 import BeautifulSoup
import os
import pathlib
import time
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
    raise AssertionError(f"{name} - Failed to raise anything, not even '{e_class}'")
  except AssertionError as e:
    raise e
  except Exception as e:
    assert type(e) == e_class
    assert e_string in str(e)

def poll_thread_is_alive(is_alive: bool, thread):
  count = 20
  while(thread.is_alive() != is_alive):
    count -= 1
    time.sleep(0.1)
    if count == 0: raise TimeoutError(f"thread failed to {is_alive}")
  return True

def soapify_mock_response(filepath: str) -> str:
  return BeautifulSoup((pathlib.Path(__file__) / '..' / filepath).resolve().read_text('UTF-8'), 'html.parser')
