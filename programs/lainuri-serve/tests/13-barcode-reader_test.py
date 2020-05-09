#!/usr/bin/python3

import context

import sys
import time
import unittest.mock

import lainuri.barcode_reader
from lainuri.barcode_reader.model.WGC_commands import *
import lainuri.event
import lainuri.event_queue
import lainuri.exception
import lainuri.websocket_server

thread_wait_sleep = 0.5

def tezt_manually_barcode_reader():
  bcr = lainuri.barcode_reader.get_BarcodeReader()

  print("Manually read a barcode now:", file=sys.stderr)
  barcode = bcr.blocking_read()

  assert barcode == ''


def mock_read_one_barcode_generator():
  mock_dispatched = 0
  def blocking_read():
    nonlocal mock_dispatched
    if not mock_dispatched:
      mock_dispatched += 1
      return 'mocked-barcode-read'
    return None
  return blocking_read

def test_barcode_reader_polling_loop(subtests, caplog):
  assert lainuri.event_queue.flush_all()
  with unittest.mock.patch.object(lainuri.barcode_reader.BarcodeReader, 'read_barcode_blocking', side_effect=mock_read_one_barcode_generator()) as blocking_read_mock:
    bcr = None

    with subtests.test("Given a mocked barcode reader"):
      bcr = lainuri.barcode_reader.init(lainuri.websocket_server.handle_barcode_read)

    with subtests.test("When the barcode polling starts"):
      bcr.start_polling_barcodes()
      assert context.poll_thread_is_alive(True, bcr.daemon)
      time.sleep(thread_wait_sleep)

    with subtests.test("And a barcode is read"):
      blocking_read_mock.assert_called()

    with subtests.test("Then the default handler is called with the read barcode"):
      event = lainuri.event_queue.history[0]
      assert type(event) == lainuri.event.LEBarcodeRead
      assert event.barcode == 'mocked-barcode-read'

    with subtests.test("And the polling thread has captured no exceptions"):
      assert 'Polling barcodes received an exception' not in ' '.join([''.join(str(t)) for t in caplog.record_tuples])

    with subtests.test("Finally the polling thread is terminated"):
      bcr.stop_polling_barcodes()
      assert context.poll_thread_is_alive(False, bcr.daemon)

def test_barcode_reader_polling_loop_exception_handling(subtests, caplog):
  with unittest.mock.patch.object(lainuri.barcode_reader.BarcodeReader, 'read_barcode_blocking', side_effect=lainuri.exception.ILS()) as blocking_read_mock:
    bcr = None

    with subtests.test("Given a mocked barcode reader that has a crashing handler"):
      bcr = lainuri.barcode_reader.get_BarcodeReader()

    with subtests.test("When the barcode polling starts"):
      bcr.start_polling_barcodes()
      assert context.poll_thread_is_alive(True, bcr.daemon)
      time.sleep(thread_wait_sleep)

    with subtests.test("And a barcode is read"):
      blocking_read_mock.assert_called()

    with subtests.test("And the polling thread captures the exception"):
      assert 'lainuri.exception.ILS' in ' '.join([''.join(str(t)) for t in caplog.record_tuples])

    with subtests.test("And the polling thread endures the Exception and keeps on polling"):
      time.sleep(thread_wait_sleep) # Give some time to die
      assert bcr.daemon.is_alive()

    with subtests.test("Finally the polling thread is terminated"):
      bcr.stop_polling_barcodes()
      assert context.poll_thread_is_alive(False, bcr.daemon)
