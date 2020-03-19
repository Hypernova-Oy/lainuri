#!/usr/bin/python3

def test_validate_config():
  import context # Behind the scenes the test context wrapper already loads lainuri.config
  import lainuri.config
  assert lainuri.config.get_config('server.hostname')
