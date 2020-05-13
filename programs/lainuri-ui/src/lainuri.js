import {Lainuri} from './lainuri-0.0.1'
import {LERingtonePlay, LERingtonePlayComplete,
  LEConfigWrite, LEUserLoggingIn,
  LEServerConnected, LEServerStatusRequest, LEException,
  LELogSend, LELogReceived} from './lainuri_events'

import {logger_manager} from './logger'
let log = logger_manager.getLogger('lainuri.js');

// Keep track of active pending events that need to be canceled.
let events = {};


const lainuri_ws = new Lainuri('ws://localhost:53153');
window.addEventListener("beforeunload", function(e){
  logger_manager.websocketAppenderInstance.sendMessageQueue();
}, false);
let interval_server_status_polling = 0;


function start_ws () {
  lainuri_ws.attach_event_listener(LEException, this, function(event) {
    if (log.isTraceEnabled()) log.trace(`Event 'LEException' received!`, event, event.exception);
  });
  lainuri_ws.attach_event_listener(LERingtonePlay, this, function(event) {
    if (log.isTraceEnabled()) log.trace(`Event 'LERingtonePlay' triggered.`);
  });
  lainuri_ws.attach_event_listener(LERingtonePlayComplete, this, function(event) {
    if (log.isTraceEnabled()) log.trace(`Event 'LERingtonePlayComplete' triggered.`);
    document.getElementById('rtttl_console').innerHTML("Finished playing: " + event.message);
  });
  lainuri_ws.attach_event_listener(LEConfigWrite, this, function(event) {
    if (log.isTraceEnabled()) log.trace(`Event 'LEConfigWrite' triggered.`);
  });
  lainuri_ws.attach_event_listener(LELogReceived, this, function(event) {
    if (log.isTraceEnabled()) log.trace(`Event 'LELogReceived' triggered.`);
  });
  lainuri_ws.attach_event_listener(LEServerConnected, this, function(event) {
    if (log.isTraceEnabled()) log.trace(`Event 'LEServerConnected' triggered.`);
  });

  lainuri_ws.open_websocket_connection();

  if (! interval_server_status_polling) {
    interval_server_status_polling = window.setInterval(() => lainuri_ws.dispatch_event(
      new LEServerStatusRequest()
    ), 10000);
  }

  logger_manager.setWebsocketHandlers((log_records_chunk) => {
    if (lainuri_ws.ws.readyState == WebSocket.OPEN) {
      lainuri_ws.dispatch_event(
        new LELogSend(log_records_chunk),
      );
      return true;
    }
    return false;
  });
}


function play_rtttl() {
  let ringtone = document.getElementById('rtttl_ringtone');
  let play_event = new LERingtonePlay(undefined, ringtone, 'client', 'server');
  // Persist reference to the event which is pending for the completion message from the server
  events[play_event.event_id] = play_event;
  lainuri_ws.dispatch_event(play_event);
}

function send_user_logging_in() {
  let event = new LEUserLoggingIn(undefined, undefined, 'client', 'server');
  // Persist reference to the event which is pending for the completion message from the server
  events[event.event_id] = event;
  lainuri_ws.dispatch_event(event);
}

export {start_ws, lainuri_ws, send_user_logging_in}