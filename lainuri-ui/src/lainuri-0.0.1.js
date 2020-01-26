'use strict';

/**
 * @version 0.0.1
 *
 * Lainuri Client implementation
 * for more documentation about possible request-response pairs, see the Swagger-UI in
 * @see <hetula-hostname>/api/v1/doc/
 *
 * Repository
 * @see {@link https://github.com/hypernova/lainuri}
 *
 * @license GPL3+
 * @copyright Hypernova Oy
 */

import * as events from './lainuri_events'
let eventname_to_eventclass = {};
Object.keys(events).map(key => {
    let eventname = events[key].event;
    eventname_to_eventclass[eventname] = events[key];
});

function ParseEventFromWebsocketMessage(raw_data, sender = undefined, recipient = undefined) {
  let data = JSON.parse(raw_data);
  let message = data.message;
  let event = data.event;
  let event_class = eventname_to_eventclass[event];
  if (! event_class) {throw new Error(`Event '${event}' doesn't map to a event class`)}
    let event_id = data.event_id;
  if (! event_id) { throw new Error(`Event '${raw_data}' is missing event_id!`) }

  let instance_data = [sender, recipient, event_id];
  let parameters = event_class.serializable_attributes.reduce((reducer, key, i) => {reducer.push(message[key]); return reducer;}, []);
  let instance = new event_class(...parameters, ...instance_data);

  // Inject the raw data payload for debugging purposes
  if (raw_data) { instance.raw_data = raw_data }
  return instance;
}

class Lainuri {

  /**
   * Keep track of event lifecycles here.
   * This is needed to trigger lifecycle hooks on pending events.
   */
  events = {};

  base_url;
  ws;
  config;
  listeners = new Map();

  constructor(base_url = 'ws://localhost:53153') {
    this.base_url = base_url;

    // The connected websocket immediately responds with configuration and inventory status
    // So we need to define the listeners in advance
    this.attach_event_listener(events.LEConfigGetpublic_Response, this, (event) => {
      this.config = event.config;
      console.log(`Received new configurations():> '${event.config}'`, event);
    });
  }

  open_websocket_connection() {
    this.ws = new WebSocket(this.base_url);
    this.ws.onopen = (event) => {
      try {
        this.dispatch_event(new events.LEServerConnected());
      }
      catch(e) {
        console.error(e)
        this.dispatch_event(new events.LEException(e, 'client', 'server'));
      }
    }
    this.ws.onclose = (event) => {
      try {
        this.dispatch_event(new events.LEServerDisconnected());
      }
      catch(e) {
        this.dispatch_event(new events.LEException(e, 'client', 'server'));
      }
    }
    this.ws.onmessage = (event) => {
      try {
        console.log("Lainuri - ws.onmessage()", event);
        this.dispatch_event(ParseEventFromWebsocketMessage(event.data, 'server', 'client'));
      }
      catch(e) {
        this.dispatch_event(new events.LEException(e, 'client', 'server'));
      }
    }
    this.ws.onerror = (event) => {
      console.error(event);
      this.dispatch_event(new events.LEException(new Error(event.data), 'client', 'server'))
    }
    return this.ws;
  }

  attach_event_listener(event, component, event_handler) {
    console.log(`Registering new event listener for event '${event.event}'`);
    if (! this.listeners[event.event]) { this.listeners[event.event] = [] }
    this.listeners[event.event].push({handler: event_handler, component: component});
    return this;
  }

  flush_listeners_for_component(component, name) {
    console.log(`Flushing events for component '${name}'`)
    Object.keys(this.listeners).forEach((event_type) => {
      let event_listeners = this.listeners[event_type];
      for (let i=0 ; i<event_listeners.length ; i++) {
        if (event_listeners[i].component === component) {
          console.log(`Flushing event '${event_type}'`)
          event_listeners.splice(i--, 1);
        }
      }
    });
  }

  dispatch_event(event) {
    let dispatched_times = 0

/*    if (this.events[event.event_id]) {
      // we receive events to an existing event and trigger lifecycle hooks
      event.lifecycle_reached(event);
    }
    else {
      this.events[event.event_id] = event;
    }*/


    if (this.listeners[event.event]) {
      this.listeners[event.event].forEach(listener => {
        dispatched_times++;
        console.log(`dispatch_event():> Receiving '${event.event}'`)
        listener.handler.call(listener.component, event);
      });
    }
    if (event.recipient === 'server' || event.default_dispatch === 'server') {
      dispatched_times++;
      let payload = event.serialize_for_ws();
      console.log(`dispatch_event():> Sending '${payload}'`)
      this.ws.send(payload);
      event.lifecycle_reached('ondispatched');
    }
    else { // Event is not sent away but received instead. Trigger lifecycle hooks
      //event.lifecycle_reached('ondispatched');
    }
    if (! dispatched_times) {
      console.log(`Receiving event '${event.event_id}', but no event handler registered?`);
    }
  }
}

export {Lainuri}
