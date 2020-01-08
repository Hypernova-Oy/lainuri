from websocket import WebSocket, WebSocketApp
import websocket

try:
  import thread
except ImportError:
  import _thread as thread
import time
import json


def test_run(ws: WebSocket, string: str =''):
  ws.send(json.dumps({
    'event': 'ringtone-play',
    'ringtone_type': 'success',
  }))
  ws.send(json.dumps({
    'event': 'ringtone-play',
    'ringtone': 'ToveriAccessGranted:d=4,o=5,b=100:32c5,32b4,32c5,4d5',
  }))
  ws.send(json.dumps({
    'event': 'config-getpublic',
  }))


def on_message(ws: WebSocket, message):
  print(message)

def on_error(ws: WebSocket, error):
  print(error)

def on_close(ws: WebSocket):
  print("### closed ###")

def on_open(ws: WebSocket):
  thread.start_new_thread(test_run, (ws,''))


if __name__ == "__main__":
    websocket.enableTrace(True)
    ws = WebSocketApp(
      "ws://localhost:12345/",
      on_message = on_message,
      on_error = on_error,
      on_close = on_close
    )
    ws.on_open = on_open
    ws.run_forever()
