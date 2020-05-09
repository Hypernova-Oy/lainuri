#!/usr/bin/python3

import context

import time

import lainuri.event
import lainuri.event_queue
import lainuri.websocket_server

def test_event_queue_thread(subtests, caplog):
  with subtests.test("Given an Event Queue polling thread"):
    event_thr = lainuri.event_queue.init(event_handler=lainuri.websocket_server.handle_one_event_daemon)
    event_thr.start()

  with subtests.test("When events are received"):
    lainuri.event_queue.push_event(lainuri.event.LEServerStatusRequest())
    time.sleep(1) # Give some time to process

  with subtests.test("Then events are handled"):
    assert 'Handling event' in ' '.join([''.join(str(t)) for t in caplog.record_tuples])

  with subtests.test("Finally the event handling thread is killed"):
    event_thr.kill()
    event_thr.join(5)
    assert not event_thr.is_alive()
