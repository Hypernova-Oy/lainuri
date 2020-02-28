from pprint import pformat

class DataElement():
  def __init__(self, offset_bytes, compaction_type_code, object_identifier, sequence, data, compacted_data, length_of_compacted_data):
    self.offset_bytes=offset_bytes,
    self.compaction_type_code=compaction_type_code
    self.object_identifier=object_identifier
    self.sequence=sequence
    self.data=data
    self.compacted_data=compacted_data,
    self.length_of_compacted_data=length_of_compacted_data,
  def __repr__(self):
    return pformat(self.__dict__)

class DataObject():
  def __init__(self):
    self.data_elements = []
  def __repr__(self):
    return pformat(self.__dict__)

  def add_data_element(self, data_element: DataElement):
    self.data_elements.append(data_element)

  def get_data_element(self, oid: int) -> DataElement:
    for de in self.data_elements:
      if de.object_identifier == oid:
        return de

class ByteStream():
  def __init__(self, byttes: bytes):
    self.byttes = byttes
    self.i = -1

  def current(self):
    return self.byttes[self.i]

  def has_next(self):
    return True if len(self.byttes) > self.i+1 else False

  def next(self):
    self.i = self.i + 1
    return self.byttes[self.i]

  def peek(self):
    return self.byttes[self.i+1]

  def previous(self):
    self.i = self.i - 1
    return self.byttes[self.i]

  def slurp(self, n: int):
    byttes = self.byttes[self.i+1 : self.i+n+1]
    self.i = self.i + n
    return byttes
