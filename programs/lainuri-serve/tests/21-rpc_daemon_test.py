#!/usr/bin/python3

import context

import lainuri.rpc_daemon
import lainuri.event
import lainuri.event_queue

import rpyc.utils.classic

def test_read_virtual_barcode(subtests):
  conn = None
  lainuri.config.write_config('server.rpc-daemon.enabled', True)
  lainuri.config.write_config('server.rpc-daemon.service-impl', 'VirtualBarcodeService')
  lainuri.event_queue.flush_all()

  with subtests.test("Given the rpc server is started"):
    lainuri.rpc_daemon.start_daemon()

  with subtests.test("And a rpc connection is established via a unix domain socket"):
    conn = rpyc.connect(host="localhost", port=59998)

  with subtests.test("When a virtual barcode is read"):
    conn.root.read_virtual_barcode('123456')

  with subtests.test("Then a LEReadBarcode-event is generated"):
    event = lainuri.event_queue.history[0]
    assert type(event) == lainuri.event.LEBarcodeRead
    assert event.barcode == '123456'

  with subtests.test("Finally the rpc server is closed"):
    assert lainuri.rpc_daemon.stop_daemon()
    lainuri.rpc_daemon.get_daemon().join(10)

def test_complete_slace_rpc_server(subtests):
  conn = None
  lainuri.config.write_config('server.rpc-daemon.enabled', True)
  lainuri.config.write_config('server.rpc-daemon.service-impl', 'SlaveService')
  lainuri.event_queue.flush_all()

  with subtests.test("Given the rpc server is started"):
    lainuri.rpc_daemon.start_daemon()

  with subtests.test("And a rpc connection is established via a unix domain socket"):
    conn = rpyc.classic.unix_connect('lainuri_rpc.sock')

  with subtests.test("When a virtual barcode is read"):
    conn.modules['lainuri.websocket_server'].handle_barcode_read(None, '123456')

  with subtests.test("Then a LEReadBarcode-event is generated"):
    event = lainuri.event_queue.history[0]
    assert type(event) == lainuri.event.LEBarcodeRead
    assert event.barcode == '123456'

  with subtests.test("Finally the rpc server is closed"):
    assert lainuri.rpc_daemon.stop_daemon()
    lainuri.rpc_daemon.get_daemon().join(10)
