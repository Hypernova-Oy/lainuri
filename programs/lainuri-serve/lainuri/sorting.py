"""
Sorting module to decide where to place the checked-in Item
"""

from lainuri.config import get_config
from lainuri.logging_context import logging
log = logging.getLogger(__name__)

from lainuri.constants import SortBin, Status

def sort(status, states):
  log.debug("Sorting status='%s', states='%s'", status, states)
  if states.get('no_item', None): return SortBin.REJECT
  if status == Status.ERROR: return SortBin.ERROR

  states_keys = list(states.keys())
  if len(states_keys):
    # TODO: refactor this silly decision tree.
    if ((len(states_keys) == 1 and states.get('not_checked_out', None)) or
       (len(states_keys) == 1 and states.get('outstanding_fines', None)) or
       (len(states_keys) == 2 and states.get('outstanding_fines', None)
                              and states.get('not_checked_out', None))):
      return SortBin.OK
    else:
      return SortBin.ERROR
  return SortBin.OK
