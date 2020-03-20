#!/usr/bin/python3

def test_validate_config():
  import context # Behind the scenes the test context wrapper already loads lainuri.config
  import lainuri.config
  assert lainuri.config.get_config('server.hostname')

def test_get_public_configs():
  import lainuri.config
  import pdb; pdb.set_trace()
  assert lainuri.config.get_public_configs()
