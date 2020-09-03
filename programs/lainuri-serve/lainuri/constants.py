#from enum import Enum # Enum breaks json serializer, otherwise things work fine!

class Status():
  SUCCESS = 'SUCCESS'
  ERROR = 'ERROR'
  PENDING = 'PENDING'
  NOT_SET = 'NOT_SET'

class SortBin():
  ERROR = 'Place_to_bin_ODD'
  OK = 'Place_to_bin_OK'
  NOT_SET = 'NOT_SET'
