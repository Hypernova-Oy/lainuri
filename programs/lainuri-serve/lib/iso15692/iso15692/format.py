import re

irv_matcher = re.compile('^[\x00-\x7E]+$')
def IRV(data: str) -> str:
  if irv_matcher.search(data):
    return data
  else:
    raise ValueError(f"Data '{data}' is not a valid ISO/IEC 646 Character string")
