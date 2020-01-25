import serial
import time

from lainuri.WGCUsb300AT.model.WGC_commands import *

port = '/dev/ttyACM1'
#ser = serial.Serial(port=port, timeout=1, databits=8)
#print(ser.__dict__)
#ser.close()

#time.sleep(1)

ser = serial.Serial()
ser.baudrate = 9600
ser.parity = serial.PARITY_NONE
ser.databits = 8
ser.stopbits = 1
ser.port = port
ser.timeout = 1
ser.open()
print(ser.__dict__)



byt = b'\x08\x04\x31\x00\x26\x4C\x54\xFF\xFD\xFE'
print(byt)
byt = WGC_ScanTrigger().pack()
print(byt)
rv = ser.write(byt)
print(f"written '{rv}'")

ser.write(WGC_VersionRead().pack())
rv = ser.readline()
print(f"read '{rv}'")
