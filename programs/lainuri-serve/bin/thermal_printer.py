import usb.core
import usb.util

# find our device
dev = usb.core.find(idVendor=0x4B43, idProduct=0x3830)

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

# write the data
ep_out.write(b'\x10\x04\x01')
rv = ep_in.read(10, 100)


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
