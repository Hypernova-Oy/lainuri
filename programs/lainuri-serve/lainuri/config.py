#from lainuri.config import get_config        # these cause circular imports
#from lainuri.logging_context import logging
#log = logging.getLogger(__name__)  # Logging not yet available

import json
import jsonschema
import locale
import yaml
import os
import pathlib
import shutil
import traceback

from lainuri.helpers import get_lainuri_sources_Path, get_system_context, null_safe_lookup, slurp_json, slurp_yaml # DO NOT import OTHER lainuri.* -modules! CIRCULAR DEPENDENCY HELL!

log = None
path_to_config_file = None
config_schema = None
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
  global config_schema
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

  see the config_schema.json -> "publicProperties" for null_safe_lookup keys to include in the public config
  """
  public_config_keys = config_schema.get('publicProperties', None)
  if not public_config_keys or len(public_config_keys) == 0:
    raise Exception("Master configuration schema error: '{\"publicProperties\": "+public_config_keys+"\}\}' is not set! The config contains a whitelist of configs that can be exposed to the GUI.")
  return {key: get_config(key) for key in public_config_keys}

def persist_config():
  with open(path_to_config_file, 'w', encoding='UTF-8') as f:
    f.write(yaml.dump(c))

def write_config(variable: str, new_value: str) -> dict:
  old_value = null_safe_lookup(c, variable)
  if None == old_value:
    raise Exception(f"Trying to write a config variable '{variable}' which doesn't exist!")
  null_safe_lookup(c, variable, new_value)
  log.info(f"Replaced config '{variable}'='{old_value}' with '{new_value}'")
  return {
    'old_value': old_value,
    'new_value': new_value,
    'variable': variable,
  }

def get_ringtone(ringtone_type) -> str:
  ringtone = null_safe_lookup(c, ['devices','ringtone-player','ringtone_types',ringtone_type])
  if None == ringtone: raise Exception(f"Missing ringtone for ringtone type '{ringtone_type}'!")
  return ringtone

def get_config(lookup: str):
  return null_safe_lookup(c, lookup)

def get_lainuri_conf_dir() -> pathlib.Path:
  return pathlib.Path(os.environ.get('LAINURI_CONF_DIR'))

def image_types():
  return [
    'png' # currently only .png is supported
    ## raster types
    #'bmp','gif','heif','indd','jpg','jpeg','png', 'psd', 'raw','tiff','webp'
    ## vector types
    #'ai','eps','pdf','svg'
  ]

def image_overloads_flush():
  """
  Only used for test cases atm. Only flushes .png-files
  """
  for target_path in image_overloads_target_directories():
    for img_type in image_types():
      for file_path in target_path.glob(f"*.{img_type}"):
        if file_path.exists():
          log.debug(f"image_overloads_flush():> Removing file '{file_path}'")
          file_path.unlink()

def image_overloads_handle():
  """
  Deploys image overloads to the UI server's public images directories
  """
  ui_images = get_config('ui.images')
  if not ui_images: return
  lainuri_config_image_overloads_path = get_lainuri_conf_dir() / 'image_overloads'

  for ui_img in ui_images:
    for target_path in image_overloads_target_directories():
      target_path_stat = target_path.stat()
      if not target_path.is_dir(): target_path.mkdir(parents=True)
      src = None
      position = None
      try:
        src = pathlib.Path(ui_img['src'])
        position = target_path / (ui_img['position']+'.png')
        if not src.is_absolute(): src = lainuri_config_image_overloads_path / src
        if not src.exists():
          log.error(f"image_overloads_handle():> image src '{src}' doesn't exist?")
          continue
        if not src.is_file():
          log.error(f"image_overloads_handle():> image src '{src}' is not a file?")
          continue
        shutil.copy(src=str(src), dst=str(position))
        try:
          os.chown(path=position, uid=target_path_stat.st_uid, gid=target_path_stat.st_gid)
        except Exception as e:
          log.debug(f"Exception setting the owner of image overloads. path='{position}', uid='{target_path_stat.st_uid}', gid='{target_path_stat.st_gid}':\n  "+traceback.format_exc)

      except Exception as e:
        log.error(f"image_overloads_handle():> Trying to copy src='{src}' to '{position}' failed. {type(e).__name__}:\n  "+traceback.format_exc)

def image_overloads_target_directories():
  lainuri_ui_path = (get_lainuri_sources_Path() / '..' / 'lainuri-ui').resolve()
  return (
    lainuri_ui_path / 'public' / 'image_overloads',
    lainuri_ui_path / 'dist' / 'image_overloads'
  )

def image_overloads_get_images():
  images = []
  for target_path in image_overloads_target_directories():
    for img_type in image_types():
      for img_path in target_path.glob(f"*.{img_type}"):
        images.append(img_path)
  return images
