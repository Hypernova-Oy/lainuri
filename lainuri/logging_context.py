#from lainuri.config import get_config        # these cause circular imports
#from lainuri.logging_context import logging
#log = logging.getLogger(__name__)  # Logging not yet available

import logging
import logging.config
import os
import yaml

path_to_log_config_file = os.path.join(os.environ.get('LAINURI_CONF_DIR'), 'logging.yaml')
try:
  with open(path_to_log_config_file, 'r', encoding='UTF-8') as f:
    config = yaml.safe_load(f.read())
    logging.config.dictConfig(config)
except Exception as e:
  print(f"Failed to configure the logger from '{path_to_log_config_file}', defaulting to extra verbose")
  logging.basicConfig(level='DEBUG')
