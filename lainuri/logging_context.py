"""
Configures logging

Reads the logging configuration yaml-file and replaces variables
using Python3's format strings, aka. f'' or str.format()
to do variable substitution
"""
#from lainuri.config import get_config        # these cause circular imports
#from lainuri.logging_context import logging
#log = logging.getLogger(__name__)  # Logging not yet available

import coloredlogs
import logging
import logging.config
import os
import traceback
import yaml

path_to_log_config_file = os.path.join(os.environ.get('LAINURI_CONF_DIR'), 'logging.yaml')
if not os.path.exists(os.environ.get('LAINURI_LOG_DIR')):
  print(f"Creating log dir '{os.environ.get('LAINURI_LOG_DIR')}'")
  os.mkdir(os.environ.get('LAINURI_LOG_DIR'))

try:
  with open(path_to_log_config_file, 'r', encoding='UTF-8') as f:
    text = f.read()
    ## Introduce logging config variables ##
    text = text.format(
      lainuri_log_dir=os.environ.get('LAINURI_LOG_DIR'),
    )
    config = yaml.safe_load(text)
    logging.config.dictConfig(config)
    coloredlogs.install(logging.DEBUG)
except Exception as e:
  print(f"Failed to configure the logger from '{path_to_log_config_file}', defaulting to extra verbose\n{traceback.format_exc()}")
  logging.basicConfig(level='DEBUG')
