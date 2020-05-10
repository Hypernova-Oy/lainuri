import pprint

def pformat(*args, **kwargs):
  if not getattr(kwargs, 'width', None): kwargs['width'] = 180
  return pprint.pformat(*args, **kwargs)
