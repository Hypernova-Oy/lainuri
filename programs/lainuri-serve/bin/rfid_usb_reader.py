import sys
sys.path.insert(0, __file__+'/../..')

import usb.core
import usb.util

# find our device
dev = usb.core.find(idVendor=0xFFFE, idProduct=0x0091)

# was it found?
if dev is None:
    raise ValueError('Device not found')


c = 1
for config in dev:
    print('config', c)
    print('Interfaces', config.bNumInterfaces)
    for i in range(config.bNumInterfaces):
        if dev.is_kernel_driver_active(i):
            dev.detach_kernel_driver(i)
        print(i)
    c+=1







# set the active configuration. With no arguments, the first
# configuration will be the active one
dev.set_configuration()

# get an endpoint instance
cfg = dev.get_active_configuration()
intf = cfg[(0,0)]

ep_out = usb.util.find_descriptor(
    intf,
    # match the first OUT endpoint
    custom_match = \
    lambda e: \
        usb.util.endpoint_direction(e.bEndpointAddress) == \
        usb.util.ENDPOINT_OUT)

assert ep_out is not None

ep_in = usb.util.find_descriptor(
    intf,
    # match the first OUT endpoint
    custom_match = \
    lambda e: \
        usb.util.endpoint_direction(e.bEndpointAddress) == \
        usb.util.ENDPOINT_IN)

assert ep_in is not None



msg = 'test'
assert dev.ctrl_transfer(0x40, usb.CTRL_LOOPBACK_WRITE, 0, 0, msg) == len(msg)
ret = dev.ctrl_transfer(0xC0, usb.CTRL_LOOPBACK_READ, 0, 0, len(msg))
sret = ''.join([chr(x) for x in ret])
assert sret == msg










#self.write(SBlock_RESYNC())
#SBlock_RESYNC_Response(self.read(SBlock_RESYNC_Response))

# write the data
from lainuri.RL866.sblock import SBlock_RESYNC, SBlock_RESYNC_Response
from lainuri.RL866.iblock import IBlock_ReadSystemConfigurationBlock, IBlock_ReadSystemConfigurationBlock_Response, IBlock_TagInventory, IBlock_TagInventory_Response, IBlock_TagConnect, IBlock_TagConnect_Response, IBlock_TagDisconnect, IBlock_TagDisconnect_Response, IBlock_TagMemoryAccess, IBlock_TagMemoryAccess_Response

import pdb; pdb.set_trace()

ep_out.write(SBlock_RESYNC().pack())
try:
  rv = ep_in.read(1)
except:
  pass

rv = ep_in.read(1)
rv2 = SBlock_RESYNC_Response(rv)

import pdb; pdb.set_trace()



#TODO: Show paper status in the GUI

class HSK_PrinterStatus():
  def __init__(self, usb_ep_out, usb_ep_in):
    usb_ep_out.write(b'\x10\x04\x01', 100)
    rv = usb_ep_in.read(10, 100)

    status = {}
    if rv & 64 == 1:
      status['paper_not_torn_away']
    return status

class HSK_PaperSensorStatus():
  def __init__(self, usb_ep_out, usb_ep_in):
    usb_ep_out.write(b'\x10\x04\x04', 100)
    rv = usb_ep_in.read(10, 100)

    status = {}
    if rv & 64 == 1:
      status['paper_out'] = 1
    if rv & 8 == 1:
      status['paper_near_out'] = 1
    return status
