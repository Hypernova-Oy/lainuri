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
      "event": "barcode-read",
      "message": {
        "barcode": "0xe00401003f3827a7"
      },
      "event_id": "barcode-read-3"
    }""",
    'client'
  )
  assert event
  assert event.event == 'barcode-read'
  assert event.barcode == '0xe00401003f3827a7'
