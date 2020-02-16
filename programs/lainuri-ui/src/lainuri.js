import {Lainuri} from './lainuri-0.0.1'
import {LEvent,
  LEBarcodeRead, LERingtonePlay, LERingtonePlayed,
  LEConfigGetpublic, LEConfigGetpublic_Response,
  LEConfigWrite,
  LEUserLoggedIn, LEUserLoggingIn, LEUserLoginAbort, LEUserLoginFailed,
  LERFIDTagsLost, LERFIDTagsNew, LERFIDTagsPresent, LEServerConnected, LEServerStatusRequest, LEException,
  LETestMockDevices} from './lainuri_events'

// Keep track of active pending events that need to be canceled.
let events = {};


const lainuri_ws = new Lainuri('ws://localhost:53153');
let interval_server_status_polling = 0;


function start_ws () {
  lainuri_ws.attach_event_listener(LEException, this, function(event) {
    console.log(`Event '${LEException.name}' received!`, event, event.exception);

    if (events[event.event_id]) {
      // If this exception-event is for the "ringtone playing" -event, we can notify the UI that the event
      // has failed.
      if (event.event_id.indexOf(LERingtonePlayed.event)) {
        document.getElementById('rtttl_console').innerHTML(event.message);
      }
    }
  });
  lainuri_ws.attach_event_listener(LERingtonePlay, this, function(event) {
    console.log(`Event '${LERingtonePlay.name}' triggered.`);
  });
  lainuri_ws.attach_event_listener(LERingtonePlayed, this, function(event) {
    console.log(`Event '${LERingtonePlayed.name}' triggered.`);
    document.getElementById('rtttl_console').innerHTML("Finished playing: " + event.message);
  });
  lainuri_ws.attach_event_listener(LEConfigWrite, this, function(event) {
    console.log(`Event '${LEConfigWrite.name}' triggered.`);
  });
  lainuri_ws.attach_event_listener(LEServerConnected, this, function(event) {
    console.log(`Event '${LEServerConnected.name}' triggered.`);
/*
    lainuri_ws.dispatch_event(
      //new LERingtonePlay('success', undefined, 'client', 'server')
      new LERingtonePlay(undefined, 'ToveriAccessGranted:d=4,o=5,b=100:32c5,32b4,32c5,4d5', 'client', 'server')
    );
    lainuri_ws.dispatch_event(
      new LEConfigWrite('missing.variable', 'bad-value', 'client', 'server')
    );
    lainuri_ws.dispatch_event(
      new LETestMockDevices()
    );
*/
  });

  lainuri_ws.open_websocket_connection();

  if (! interval_server_status_polling) {
    interval_server_status_polling = window.setInterval(() => lainuri_ws.dispatch_event(
      new LEServerStatusRequest()
    ), 30000);
  }
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