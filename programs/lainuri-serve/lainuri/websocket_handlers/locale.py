from lainuri.config import get_config
from lainuri.logging_context import logging
log = logging.getLogger(__name__)

import lainuri.locale

def set_locale(event):
  lainuri.locale.set_locale(event.locale_code)
