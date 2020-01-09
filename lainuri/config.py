import yaml
import os

## Do the bare minimums here to read the most rudimentary configuration, before logging can be set up.
def validate_environment():
  print("Lainuri ENV:")
  if not os.environ.get('LAINURI_CONF_DIR'):
    print(f"Environment variable LAINURI_CONF_DIR is not set, looking for config from cwd '{os.getcwd()}'")
    os.environ.update({'LAINURI_CONF_DIR': './config/'})
  print(f"  LAINURI_CONF_DIR='{os.environ.get('LAINURI_CONF_DIR')}'")
validate_environment()

path_to_config_file = os.path.join(os.environ.get('LAINURI_CONF_DIR'), 'config.yaml')
def load_config():
  with open(path_to_config_file, 'r', encoding='UTF-8') as f:
    return yaml.safe_load(f.read())
c = load_config()

def persist_config():
  with open(path_to_config_file, 'w', encoding='UTF-8') as f:
    f.write(yaml.dump(c))

from lainuri.logging_context import logging
log = logging.getLogger(__name__)

# Logging has been set up and the app is now properly operational to behave uniformly from now on.

from lainuri.helpers import null_safe_lookup

def get_public_configs() -> dict:
  """
  Whitelist the configs that can be exposed to the UI
  """
  return {
    'ringtones': c['ringtones'],
  }

def write_config(variable: str, new_value: str) -> dict:
  old_value = null_safe_lookup(c, variable)
  if None == old_value:
    raise Exception(f"Trying to write a config variable '{variable}' which doesn't exist!")
  null_safe_lookup(c, variable, new_value)
  log.info(f"Replaced config '{variable}'='{old_value}' with '{new_value}'")
  persist_config()
  return {
    'old_value': old_value,
    'new_value': new_value,
    'variable': variable,
  }

def get_ringtone(ringtone_type) -> str:
  ringtone = null_safe_lookup(c, ['ringtones', ringtone_type])
  if None == ringtone: raise Exception(f"Missing ringtone for ringtone type '{ringtone_type}'!")
  return ringtone

def get_config(lookup: str):
  return null_safe_lookup(c, lookup)
