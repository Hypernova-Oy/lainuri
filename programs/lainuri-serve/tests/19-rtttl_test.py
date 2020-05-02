#!/usr/bin/python3

import context
from lainuri.config import get_config

import pytest_subtests
import threading
import time
import unittest.mock

import lainuri.websocket_server
from lainuri.constants import Status
import lainuri.event as le


def test_rtttl_validator():
  assert lainuri.rtttl_player.rtttl_validator_re.search('Popcorn:d=4,o=5,b=160:8c6,8a#,8c6,8g,8d#,8g,c,8c6,8a#,8c6,8g,8d#,8g,c,8c6,8d6,8d#6,16c6,8d#6,16c6,8d#6,8d6,16a#,8d6,16a#,8d6,8c6,8a#,8g,8a#,c6')
  assert lainuri.rtttl_player.rtttl_validator_re.search('Scatman:d=4,o=5,b=200:8b,16b,32p,8b,16b,32p,8b,2d6,16p,16c#.6,16p.,8d6,16p,16c#6,8b,16p,8f#,2p.,16c#6,8p,16d.6,16p.,16c#6,16b,8p,8f#,2p,32p,2d6,16p,16c#6,8p,16d.6,16p.,16c#6,16a.,16p.,8e,2p.,16c#6,8p,16d.6,16p.,16c#6,16b,8p,8b,16b,32p,8b,16b,32p,8b,2d6,16p,16c#.6,16p.,8d6,16p,16c#6,8b,16p,8f#,2p.,16c#6,8p,16d.6,16p.,16c#6,16b,8p,8f#,2p,32p,2d6,16p,16c#6,8p,16d.6,16p.,16c#6,16a.,16p.,8e,2p.,16c#6,8p,16d.6,16p.,16c#6,16a,8p,8e,2p,32p,16f#.6,16p.,16b.,16p.')
  assert not lainuri.rtttl_player.ringtone_type_songname_parser.match('ToveriAccessDenied:d=4,o=4,b=100:32e,32d,32e,4c')
  assert lainuri.rtttl_player.ringtone_type_songname_parser.match('ToveriAccessDenied')


def test_list_rtttl(subtests):
  assert lainuri.event_queue.flush_all()
  event = None
  event_response = None

  with subtests.test(f"Given an LERingtoneList-event"):
    event = le.LERingtoneList()

  with subtests.test("When the event is dispatched"):
    lainuri.event_queue.push_event(event)
    assert lainuri.websocket_server.handle_one_event(5) == event
    assert event == lainuri.event_queue.history[0]
    time.sleep(2)

  with subtests.test("Then a response event is generated"):
    event_response = lainuri.websocket_server.handle_one_event(5)
    assert event_response == lainuri.event_queue.history[1]
    assert type(event_response) == le.LERingtoneListResponse
    assert event_response.states == {}
    assert event_response.status == Status.SUCCESS


def test_play_rtttl_checkin_out_types(subtests):
  lainuri.config.write_config('devices.ringtone-player.enabled', True)
  with unittest.mock.patch.object(lainuri.rtttl_player, 'play_rtttl', side_effect=lainuri.rtttl_player.play_rtttl) as play_rtttl_mock:

    player_thr = threading.Thread(group=None, target=lainuri.rtttl_player.rtttl_daemon)
    player_thr.start()

    run_play_rtttl_tst(subtests, play_rtttl_mock, 'checkout-error')
    run_play_rtttl_tst(subtests, play_rtttl_mock, 'checkout-success')
    run_play_rtttl_tst(subtests, play_rtttl_mock, 'checkin-error')
    run_play_rtttl_tst(subtests, play_rtttl_mock, 'checkin-success')
    run_play_rtttl_tst(subtests, play_rtttl_mock, None, 'Popcorn:d=4,o=5,b=160:8c6,8a#,8c6,8g,8d#,8g,c,8c6,8a#,8c6,8g,8d#,8g,c,8c6,8d6,8d#6,16c6,8d#6,16c6,8d#6,8d6,16a#,8d6,16a#,8d6,8c6,8a#,8g,8a#,c6')

    lainuri.rtttl_player.kill = 1
    player_thr.join(timeout=5)
    assert not player_thr.is_alive()

def run_play_rtttl_tst(subtests, play_rtttl_mock, ringtone_type = None, ringtone = None):
  assert lainuri.event_queue.flush_all()
  event = None
  event_response = None

  with subtests.test(f"Given an LERingtonePlay-event for {ringtone_type}"):
    event = le.LERingtonePlay(ringtone_type=ringtone_type, ringtone=ringtone)

  with subtests.test("When the event is dispatched"):
    lainuri.event_queue.push_event(event)
    assert lainuri.websocket_server.handle_one_event(5) == event
    assert event == lainuri.event_queue.history[0]
    time.sleep(2)

  with subtests.test("Then a response event is generated"):
    event_response = lainuri.websocket_server.handle_one_event(5)
    assert event_response == lainuri.event_queue.history[1]
    assert type(event_response) == le.LERingtonePlayComplete
    assert event_response.ringtone_type == event.ringtone_type
    assert event_response.states == {}
    assert event_response.status == Status.SUCCESS

  with subtests.test("And the play_rtttl -subsystem interface was triggered"):
    play_rtttl_mock.assert_called_with(event)
