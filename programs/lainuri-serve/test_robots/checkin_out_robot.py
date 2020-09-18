"""
IN THIS FILE

This robot checks in and out Items on the RFID reader.
It reads a virtual barcode, to identify the logging in user, by using the lainuri rpc-service.

"""
import datetime
import os
import pathlib
import rpyc
from selenium import webdriver
from selenium.common.exceptions import ElementNotVisibleException, TimeoutException
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.touch_actions import TouchActions
from selenium.webdriver.support.wait import WebDriverWait
import time

import logging
logging.basicConfig(level=logging.INFO)
log = logging.getLogger()


if not 'DISPLAY' in os.environ: os.environ['DISPLAY'] = ':0'


loop_times = 2
checkout_user_barcode = '2600104874'
item_barcodes = [
  '9781491980552',
  '2600104874',
  '167A0174667',
]

geckopath=str((pathlib.Path(__file__) / '..' / 'geckodriver').resolve())

class LainuriRobot():
  def __init__(self, url, user_barcode, item_barcodes=[]):
    self.user_barcode = user_barcode
    self.item_barcodes = item_barcodes

    self.driver = webdriver.Firefox(executable_path=geckopath, service_log_path='/tmp/geckodriver.log')
    self.driver.set_window_position(0,0)
    self.driver.set_window_size(1080, 1920)
    self.driver.get(url)
    assert 'lainuri-web' in self.driver.title

    self.rpyc = rpyc.connect(host="localhost", port=59998)

  def checkin(self):
    checkin_mode_button = self.driver.find_element_by_id('checkin_mode_button')  # Find the search box
    assert checkin_mode_button.is_displayed()
    self._click(checkin_mode_button)

    # Checkout books using virtual barcode reading
    for bc in self.item_barcodes:
      time.sleep(0.25)
      self.rpyc.root.read_virtual_barcode(bc)
    time.sleep(len(self.item_barcodes) * 2)

    try:
      while True:
        overlay_notification = self._wait_for_element('find_element_by_class_name', "close-overlay-icon")
        self._click(overlay_notification)
    except Exception as e:
      if type(e) != TimeoutException:
        log.exception(e)

    finish_with_receipt_button = self._wait_for_element('find_element_by_id', "finish_with_receipt_button", timeout=60)
    self._click(finish_with_receipt_button)

    self._wait_for_element('find_element_by_class_name', "main-menu-view", timeout=30)

  def checkout(self):
    checkout_mode_button = self.driver.find_element_by_id('checkout_mode_button')  # Find the search box
    assert checkout_mode_button.is_displayed()
    self._click(checkout_mode_button)

    # Login
    time.sleep(0.25)
    self.rpyc.root.read_virtual_barcode(self.user_barcode)

    # Checkout books using virtual barcode reading
    for bc in self.item_barcodes:
      time.sleep(0.25)
      self.rpyc.root.read_virtual_barcode(bc)
    time.sleep(len(self.item_barcodes) * 3)

    try:
      while True:
        overlay_notification = self._wait_for_element('find_element_by_class_name', "close-overlay-icon")
        self._click(overlay_notification)
    except Exception as e:
      if type(e) != TimeoutException:
        log.exception(e)

    finish_with_receipt_button = self._wait_for_element('find_element_by_id', "finish_with_receipt_button", timeout=60)
    self._click(finish_with_receipt_button)

    self._wait_for_element('find_element_by_class_name', "main-menu-view", timeout=30)

  def _click(self, element):
    self._action_chain_perform([['click', element]])

  def _wait_for_element(self, find_method, selector, timeout=5, poll_frequency=0.5):
    method = getattr(self.driver, find_method, None)
    if not method: raise ValueError(f"_wait_for_element() WebDriver missing method '{find_method}' with selector '{selector}'")

    return WebDriverWait(driver=self.driver, timeout=timeout, poll_frequency=poll_frequency).until(lambda x: method(selector))

  def _action_chain_perform(self, actions):
      action_chain = ActionChains(self.driver)
      for a in actions:
        method = getattr(action_chain, a[0], None)
        if not method: raise ValueError(f"ActionChain() method '{a[0]}' doesn't exist!")
        method(*a[1:])
      action_chain.perform()

robot = LainuriRobot('http://localhost:5000', user_barcode=checkout_user_barcode, item_barcodes=item_barcodes)
try:
  robot.rpyc.root.play_rtttl('ToveriAccessDenied:d=4,o=4,b=100:32e,32d,32e,4c')
  for i in range(loop_times):
    robot.checkin()
    robot.checkout()
  robot.checkin()
finally:
  robot.driver.quit()
