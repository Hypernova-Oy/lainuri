import {Lainuri} from './lainuri-0.0.1'
import {LEvent,
  LEBarcodeRead, LERingtonePlay, LERingtonePlayed,
  LEConfigGetpublic, LEConfigGetpublic_Response,
  LEConfigWrite,
  LEUserLoggedIn, LEUserLoggingIn, LEUserLoginAbort, LEUserLoginFailed,
  LERFIDTagsLost, LERFIDTagsNew, LERFIDTagsPresent, LEServerConnected, LEServerDisconnected, LEException,
  LETestMockDevices} from './lainuri_events'

// Keep track of active pending events that need to be canceled.
let events = {};


let vue;
const lainuri_ws = new Lainuri('ws://localhost:53153');

function start_ws () {
  lainuri_ws.attach_event_listener(LEException, function(event) {
    console.log(`Event '${LEException.name}' received!`, event, event.exception);

    if (events[event.event_id]) {
      // If this exception-event is for the "ringtone playing" -event, we can notify the UI that the event
      // has failed.
      if (event.event_id.indexOf(LERingtonePlayed.event)) {
        document.getElementById('rtttl_console').innerHTML(event.message);
      }
    }
  });
  lainuri_ws.attach_event_listener(LEBarcodeRead, function(event) {
    console.log(`Event '${LEBarcodeRead.name}' received.`);
    vue.$data['barcode_read'] = event.barcode;
  });
  lainuri_ws.attach_event_listener(LERingtonePlay, function(event) {
    console.log(`Event '${LERingtonePlay.name}' triggered.`);
  });
  lainuri_ws.attach_event_listener(LERingtonePlayed, function(event) {
    console.log(`Event '${LERingtonePlayed.name}' triggered.`);
    document.getElementById('rtttl_console').innerHTML("Finished playing: " + event.message);
  });
  lainuri_ws.attach_event_listener(LEConfigWrite, function(event) {
    console.log(`Event '${LEConfigWrite.name}' triggered.`);
  });
  lainuri_ws.attach_event_listener(LERFIDTagsNew, function(event) {
    console.log(`Event '${LERFIDTagsNew.name}' triggered. New RFID tags:`, event.tags_new, event.tags_present);
    vue.$data['rfid_tags_present'] = event.tags_present;
  });
  lainuri_ws.attach_event_listener(LERFIDTagsLost, function(event) {
    console.log(`Event '${LERFIDTagsLost.name}' triggered. New RFID tags:`, event.tags_lost, event.tags_present);
    vue.$data['rfid_tags_present'] = event.tags_present;
  });
  lainuri_ws.attach_event_listener(LERFIDTagsPresent, function(event) {
    console.log(`Event '${LERFIDTagsPresent.name}' triggered. Present RFID tags:`, event.tags_present);
    vue.$data['rfid_tags_present'] = event.tags_present;
  });
  lainuri_ws.attach_event_listener(LEServerDisconnected, function(event) {
    console.log(`Event '${LEServerDisconnected.name}' triggered.`);
  });
  lainuri_ws.attach_event_listener(LEServerConnected, function(event) {
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
  lainuri_ws.attach_event_listener(LEUserLoggedIn, function(event) {
    console.log(`Event '${LEUserLoggedIn.name}' received.`);
    vue.$data.user.firstname = event.firstname
    vue.$data.user.surname = event.surname
    vue.$data.user.cardnumber = event.cardnumber
    vue.$data.user.password = event.password
  });
  lainuri_ws.attach_event_listener(LEUserLoginFailed, function(event) {
    console.log(`Event '${LEUserLoginFailed.name}' received.`);
    vue.$data.user.firstname = undefined;
    vue.$data.user.surname = undefined;
    vue.$data.user.cardnumber = undefined;
    vue.$data.user.password = undefined;
    vue.$data.app_mode = 'mode_main_menu';
  });
  lainuri_ws.attach_event_listener(LEUserLoginAbort, function(event) {
    console.log(`Event '${LEUserLoginAbort.name}' received.`);
    vue.$data.user.firstname = undefined;
    vue.$data.user.surname = undefined;
    vue.$data.user.cardnumber = undefined;
    vue.$data.user.password = undefined;
    vue.$data.app_mode = 'mode_main_menu';
  });


  lainuri_ws.open_websocket_connection();
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
export {start_ws, lainuri_set_vue, lainuri_ws, send_user_logging_in, abort_user_login}