import {Lainuri} from './lainuri-0.0.1'
import {LEvent,
  LEBarcodeRead, LERingtonePlay, LERingtonePlayComplete,
  LEConfigGetpublic, LEConfigGetpublic_Response,
  LEConfigWrite,
  LEUserLoginComplete, LEUserLoggingIn, LEUserLoginAbort,
  LERFIDTagsLost, LERFIDTagsNew, LERFIDTagsPresent, LEServerConnected, LEServerDisconnected, LEException,
  LETestMockDevices} from './lainuri_events'

function run_test_suite() {
  // Keep track of active pending events that need to be canceled.
  let events = {};


  let vue;
  const lainuri_ws = new Lainuri('ws://localhost:53153');

  lainuri_ws.attach_event_listener(LEException, this, function(event) {
    console.log(`Event '${LEException.name}' received!`, event, event.exception);

    if (events[event.event_id]) {
      // If this exception-event is for the "ringtone playing" -event, we can notify the UI that the event
      // has failed.
      if (event.event_id.indexOf(LERingtonePlayComplete.event)) {
        document.getElementById('rtttl_console').innerHTML(event.message);
      }
    }
  });
  lainuri_ws.attach_event_listener(LEServerConnected, this, function(event) {
    console.log(`Event '${LEServerConnected.name}' triggered.`);

    let suite = 0;
    if (suite === 1) {
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
    } else { // test login
      lainuri_ws.dispatch_event(
        new LEUserLoggingIn()
      );
      // Now read barcode
    }
  });


  lainuri_ws.open_websocket_connection();


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

  function abort_user_login() {
    let event = new LEUserLoginAbort(undefined, undefined, 'client', 'server');
    // Persist reference to the event which is pending for the completion message from the server
    events[event.event_id] = event;
    lainuri_ws.dispatch_event(event);
  }

  function lainuri_set_vue(vue_instance) {
    vue = vue_instance;
    vue.$data['barcode_read'] = 'ggggggggggggggggg';
  }
}

export {run_test_suite}
