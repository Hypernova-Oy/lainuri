import context

import lainuri.websocket_server

def test_message_parsing():
  event = lainuri.websocket_server.ParseEventFromWebsocketMessage(
    """{
      "event": "register-client",
      "message": {},
      "event_id": "register-client-2"
    }""",
    'client'
  )
  assert event
  assert event.event == 'register-client'

  event = lainuri.websocket_server.ParseEventFromWebsocketMessage(
    """{
      "event": "ringtone-played",
      "message": {
        "ringtone_type": "check-in",
        "ringtone": ""
      },
      "event_id": "ringtone-played-3"
    }""",
    'client'
  )
  assert event
  assert event.event == 'ringtone-played'
  assert event.ringtone_type == 'check-in'
