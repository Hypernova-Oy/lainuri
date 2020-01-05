from RL866.message import Message, parseMessage
import RL866.state

class SBlock(Message):
  def __init__(self, RID, PCB):
    super().__init__(RID, PCB)

class SBlock_RESYNC(SBlock):
  def __init__(self):
    super().__init__(RID=RL866.state.RID_request, PCB=bytes([int('11000000',2)]))

class SBlock_RESYNC_Response(SBlock):
    def __init__(self, resp_bytes: bytearray):
        if len(resp_bytes) != 6: raise Exception(f"${type(self)} - Response '${resp_bytes}' is not 6 bytes!")
        parseMessage(self, resp_bytes)
        super().__init__(RID=self.RID, PCB=self.PCB)
