'use strict';
Object.defineProperty(exports, "__esModule", { value: true });
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
const events = require("./events");
Object.keys(events).map(key => alert(key));
class Lainuri {
    constructor(base_url = 'ws://localhost:53153') {
        /**
         * Keep track of event lifecycles here.
         * This is needed to trigger lifecycle hooks on pending events.
         */
        this.events = {};
        this.listeners = new Map();
        this.base_url = base_url;
        // The connected websocket immediately responds with configuration and inventory status
        // So we need to define the listeners in advance
        this.attach_event_listener(events.LEConfigGetpublic_Response, (event) => {
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
            catch (e) {
                console.error(e);
                this.dispatch_event(new events.LEException(e, 'client', 'server'));
            }
        };
        this.ws.onclose = (event) => {
            try {
                this.dispatch_event(new events.LEServerDisconnected());
            }
            catch (e) {
                this.dispatch_event(new events.LEException(e, 'client', 'server'));
            }
        };
        this.ws.onmessage = (event) => {
            try {
                console.log("Lainuri - ws.onmessage()", event);
                this.dispatch_event(events.LEvent.CreateClassInstance(event.data, 'server', 'client'));
            }
            catch (e) {
                this.dispatch_event(new events.LEException(e, 'client', 'server'));
            }
        };
        this.ws.onerror = (event) => {
            console.error(event);
            this.dispatch_event(new events.LEException(new Error(event.data), 'client', 'server'));
        };
        return this.ws;
    }
    attach_event_listener(event, event_handler) {
        console.log(`Registering new event listener for event '${event.event}'`);
        if (!this.listeners[event.event]) {
            this.listeners[event.event] = [];
        }
        this.listeners[event.event].push(event_handler);
        return this;
    }
    dispatch_event(event) {
        let dispatched_times = 0;
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
                listener(event);
            });
        }
        if (event.recipient === 'server' || event.default_dispatch === 'server') {
            dispatched_times++;
            let payload = event.serialize_for_ws();
            console.log(`dispatch_event():> Sending '${payload}'`);
            this.ws.send(payload);
            event.lifecycle_reached('ondispatched');
        }
        else { // Event is not sent away but received instead. Trigger lifecycle hooks
            //event.lifecycle_reached('ondispatched');
        }
        if (!dispatched_times) {
            throw new Error(`Dispatching event '${event.event}', but no event handler registered?`);
        }
    }
}
