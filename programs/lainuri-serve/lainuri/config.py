#from lainuri.config import get_config        # these cause circular imports
#from lainuri.logging_context import logging
#log = logging.getLogger(__name__)  # Logging not yet available

import json
import jsonschema
import locale
import yaml
import os
import traceback

from lainuri.helpers import get_lainuri_sources_Path, get_system_context, null_safe_lookup, slurp_json, slurp_yaml # DO NOT import OTHER lainuri.* -modules! CIRCULAR DEPENDENCY HELL!

log = None
path_to_config_file = None
jsonschema_validator = None
c = None

########                                                                                               ########
##                                                                                                           ##
# Do the bare minimums here to read the most rudimentary configuration, before logging can be set up.         #
##                                                                                                           ##
########                                                                                               ########
locale.setlocale(locale.LC_ALL, '') # According to POSIX, a program which has not called setlocale(LC_ALL, '') runs using the portable 'C' locale. Calling setlocale(LC_ALL, '') lets it use the default locale as defined by the LANG variable. Since we do not want to interfere with the current locale setting we thus emulate the behavior in the way described above.
def validate_environment():
  global path_to_config_file
  print("Lainuri ENV:")
  if not os.environ.get('LAINURI_CONF_DIR'):
    print(f"Environment variable LAINURI_CONF_DIR is not set, looking for config from cwd '{os.getcwd()}'")
    os.environ.update({'LAINURI_CONF_DIR': './config/'})
  print(f"  LAINURI_CONF_DIR='{os.environ.get('LAINURI_CONF_DIR')}'")
  if not os.environ.get('LAINURI_LOG_DIR'):
    print(f"Environment variable LAINURI_LOG_DIR is not set, setting log dir based on cwd '{os.getcwd()}'")
    os.environ.update({'LAINURI_LOG_DIR': './logs/'})
  print(f"  LAINURI_LOG_DIR='{os.environ.get('LAINURI_LOG_DIR')}'")
  path_to_config_file = os.path.join(os.environ.get('LAINURI_CONF_DIR'), 'config.yaml')

def instantiate_jsonschema_validator():
  config_schema = slurp_json(get_lainuri_sources_Path() / 'lainuri' / 'config_schema.json')
  jsonschema_validator = jsonschema.Draft6Validator(config_schema)
  jsonschema_validator.check_schema(config_schema)
  return jsonschema_validator

try:
  validate_environment()
  jsonschema_validator = instantiate_jsonschema_validator()
  c = slurp_yaml(path_to_config_file)
  jsonschema_validator.validate(c)

  from lainuri.logging_context import logging
  log = logging.getLogger(__name__)
except Exception as e:
  raise type(e)(f"Loading configuration failed!\n  - System context='{get_system_context()}'\n  - Exception='{traceback.format_exc()}'")
########                                                                                               ########
##                                                                                                           ##
# Logging and config has been set up and the app is now properly operational to behave uniformly from now on. #
##                                                                                                           ##
########                                                                                               ########

def get_public_configs() -> dict:
  """
  Whitelist the configs that can be exposed to the UI
  """
  images = get_config('ui.images')
  if images: images = {i['position']: i for i in images}
  return {
    'ui.images': images,
    'ui.use_bookcovers': get_config('ui.use_bookcovers'),
    'i18n.default_locale': get_config('i18n.default_locale').lower(),
    'i18n.enabled_locales': get_config('i18n.enabled_locales'),
    'i18n.messages': get_config('i18n.messages'),
  }

def persist_config():
  with open(path_to_config_file, 'w', encoding='UTF-8') as f:
    f.write(yaml.dump(c))

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

