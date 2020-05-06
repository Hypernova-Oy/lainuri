from lainuri.config import get_config
from lainuri.logging_context import logging
log = logging.getLogger(__name__)

import lainuri.helpers

import atexit
import escpos
import escpos.constants
import escpos.printer
import threading
import time
import usb.core
import usb.util

printer = None # Singleton accessor

class HSK_Printer():
  """
  Python3 escpos library prevents accessing device status when using USB connection.
  This wrapper exposes escpos-librarys capabilities while enriching with custom device-specific settings.

  pr = HSK_Printer()
  pr.escpos_printer.qr(...)
  pr.escpos_printer.text("Hello world!")
  pr.transmit_status()
  """

  timeout = 1000

  def __init__(self):
    self.transaction_lock = threading.Lock()
    self._get_printer_usb_connection()
    self.initialize_printer()
    self.reconfigure()

  def reconfigure(self):
    self.set_print_concentration(
      max_printing_dots=get_config('devices.thermal-printer.printing-speed'),
      heating_time=get_config('devices.thermal-printer.printing-heat'),
      heating_interval=get_config('devices.thermal-printer.printing-precision'),
    )

  def _get_printer_usb_connection(self):
    # find our device
    dev = usb.core.find(idVendor=0x4B43, idProduct=0x3830)

    # was it found?
    if dev is None:
        raise ValueError('HS-K33: USB device not found!')

    dev.reset()

    for config in dev:
        for i in range(config.bNumInterfaces):
            if dev.is_kernel_driver_active(i): dev.detach_kernel_driver(i)

    # set the active configuration. With no arguments, the first configuration will be the active one
    dev.set_configuration()

    # get an endpoint instance
    cfg = dev.get_active_configuration()
    intf = cfg[(0,0)]

    self.usb_ep_out = usb.util.find_descriptor(
        intf,
        # match the first OUT endpoint
        custom_match = \
        lambda e: \
            usb.util.endpoint_direction(e.bEndpointAddress) == \
            usb.util.ENDPOINT_OUT)
    if not self.usb_ep_out: raise ValueError('HS-K33: USB device endpoint OUT not found!')

    self.usb_ep_in = usb.util.find_descriptor(
        intf,
        # match the first OUT endpoint
        custom_match = \
        lambda e: \
            usb.util.endpoint_direction(e.bEndpointAddress) == \
            usb.util.ENDPOINT_IN)
    if not self.usb_ep_in: raise ValueError('HS-K33: USB device endpoint IN not found!')

    self.escpos_printer = escpos.printer.Usb(idVendor=0x4B43, idProduct=0x3830, in_ep=self.usb_ep_in, out_ep=self.usb_ep_out, timeout=self.timeout)

  def _transaction(self, write_bytes: bytes, read_bytes: int = 0, read_can_timeout: bool = False, sleep: int = 0):
    """
    Thread-safety layer
    """
    with self.transaction_lock:
      self._write(write_bytes)

      resp = None
      if read_bytes:
        try:
          resp = self._read(read_bytes)
        except usb.core.USBError as e:
          if "[Errno 110] Operation timed out" in str(e):
            if not read_can_timeout: raise e
          else: raise e

    if sleep: time.sleep(sleep)

    return resp

  def _write(self, msg: bytes):
    if log.isEnabledFor(logging.DEBUG):
      log.debug(lainuri.helpers.bytes_to_hex_string(msg, f"HS-K33: _write '", "'", " "))
    return self.escpos_printer.device.write(self.usb_ep_out, msg, self.timeout)

  def _read(self, read_bytes: int = 16):
    msg = self.escpos_printer.device.read(self.usb_ep_in, read_bytes, self.timeout)
    if log.isEnabledFor(logging.DEBUG):
      log.debug(lainuri.helpers.bytes_to_hex_string(msg, f"HS-K33: _read  '", "'", " "))
    return msg

  def close(self):
    return self.escpos_printer.close()

  def escpos_method(self, method_name, *args, **kwargs):
    """
    Thread-safe version of python-escpos methods
    """
    method = getattr(self.escpos_printer, method_name, None)
    if not method: raise ValueError(f"python-escpos method '{method_name}' doesn't exist!")

    with self.transaction_lock: return method(*args, **kwargs)

  def initialize_printer(self):
    return self._transaction(b'\x1B\x40', read_bytes=1, read_can_timeout=True)

  def is_paper_torn_away(self):
    return not self.real_time_transmission_status(printer_status=True).paper_not_torn_away

  def paper_status(self):
    """
    Reimplementation of escpos paper_status()
    """
    rtts = self.real_time_transmission_status(transmission_paper_sensor_status=True)
    if rtts.paper_adequate: return 2
    if rtts.paper_ending: return 1
    if rtts.paper_out: return 0

  def paper_cut(one_point_left: bool = True, three_points_left: bool = False):
    if three_points_left: return self._transaction(b'\x1B\x6D')
    if one_point_left: return self._transaction(b'\x1B\x69')

  def real_time_transmission_status(self, printer_status=None, send_offline_status=None, transmission_error_status=None, transmission_paper_sensor_status=None):
    """
    See HS-K33 User Manual
    """
    if not printer_status and not send_offline_status and not transmission_error_status and not transmission_paper_sensor_status:
      raise ValueError('HS-K33: You must specify the status you want, atleast one!')

    rtts = HSK_RealTimeTransmissionStatus()
    if printer_status:
      rtts.printer_status(self._transaction(b'\x10\x04\x01', read_bytes=1))
    if send_offline_status:
      rtts.send_offline_status(self._transaction(b'\x10\x04\x02', read_bytes=1))
    if transmission_error_status:
      rtts.transmission_error_status(self._transaction(b'\x10\x04\x03', read_bytes=1))
    if transmission_paper_sensor_status:
      rtts.transmission_paper_sensor_status(self._transaction(b'\x10\x04\x04', read_bytes=1))
    return rtts

  def set_print_concentration(self, max_printing_dots=9, heating_time=80, heating_interval=2):
    """
    See HS-K33 User Manual.
    """
    if max_printing_dots < 0 or max_printing_dots > 255: raise ValueError(f"HS-K33: set_print_concentration max_printing_dots '{max_printing_dots}' is invalid!")
    if heating_time < 3 or heating_time > 255: raise ValueError(f"HS-K33: set_print_concentration heating_time '{heating_time}' is invalid!")
    if heating_interval < 0 or heating_interval > 255: raise ValueError(f"HS-K33: set_print_concentration heating_interval '{heating_interval}' is invalid!")

    bs = bytearray([0x1B, 0x37])
    bs.append(max_printing_dots)
    bs.append(heating_time)
    bs.append(heating_interval)

    return self._transaction(bs, read_bytes=0, sleep=0.250) # Wait a bit for the printer to set the new settings internally

  def test_page(self):
    return self._transaction(b'\x1B\x40\x12\x54', read_bytes=1, sleep=1.0)

  def transmit_status(self):
    """
    See HS-K33 User Manual.
    Use real_time_transmission_status() instead, as this timeouts on paper out
    """
    return HSK_TransmitStatus(self._transaction(b'\x1D\x72\x01', read_bytes=1))

class HSK_TransmitStatus():
  def __init__(self, bs: bytes):
    if bs[0] & 0b00110000:
      self.paper_adequate = 0
      self.paper_ending = 1
    else:
      self.paper_adequate = 1
      self.paper_ending = 0

class HSK_RealTimeTransmissionStatus():
  def __init__(self):
    pass
  def printer_status(self, bs: bytes):
    if not bs[0] & 0b00010010:
      raise ValueError(f"HS-K33: printer_status static bit map is not as expected!")
    if bs[0] & 0b00000100: self.cash_drawer_closed = True
    else: self.cash_drawer_closed = False
    if bs[0] & 0b10000000: self.paper_not_torn_away = True
    else: self.paper_not_torn_away = False
    return self
  def send_offline_status(self, bs: bytes):
    if not bs[0] & 0b00010010:
      raise ValueError(f"HS-K33: send_offline_status static bit map is not as expected!")
    if bs[0] & 0b00000100: self.paper_warehouse_open = False
    else: self.paper_warehouse_open = True
    if bs[0] & 0b00001000: self.push_feed_button = True
    else: self.push_feed_button = False
    if bs[0] & 0b00100000: self.paper_out = True
    else: self.paper_out = False
    if bs[0] & 0b01000000: self.error_status = True
    else: self.error_status = False
    return self
  def transmission_error_status(self, bs: bytes):
    if not bs[0] & 0b00010010:
      raise ValueError(f"HS-K33: transmission_error_status static bit map is not as expected!")
    if bs[0] & 0b00001000: self.cutter_error = True
    else: self.cutter_error = False
    if bs[0] & 0b00100000: self.unrecoverable_error = True
    else: self.unrecoverable_error = False
    if bs[0] & 0b01000000: self.print_head_voltage_and_temperature_over_range = True
    else: self.print_head_voltage_and_temperature_over_range = False
    return self
  def transmission_paper_sensor_status(self, bs: bytes):
    if not bs[0] & 0b00010010:
      raise ValueError(f"HS-K33: transmission_paper_sensor_status static bit map is not as expected!")
    if bs[0] & 0b00001100: self.paper_ending = True
    else: self.paper_ending = False
    if bs[0] & 0b01100000: self.paper_out = True
    else: self.paper_out = False
    if bs[0] & 0b01000000: self.print_head_voltage_and_temperature_over_range = True
    else: self.print_head_voltage_and_temperature_over_range = False

    if self.paper_out or self.paper_ending:
      self.paper_adequate = False
    else:
      self.paper_adequate = True
    return self

def get_printer() -> HSK_Printer:
  global printer
  if not printer: init()
  return printer

def init():
  global printer
  log.info("HSK_Printer init()")
  printer = HSK_Printer()
  atexit.register(lambda: printer.close())