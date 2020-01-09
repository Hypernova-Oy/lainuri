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

class LEvent {

  event: string
  message: Object;
  raw_data: string;
  sender: string;
  recipient: string;
  default_dispatch: string = undefined;
  event_id: string;

  /**
   * Overload. These attributes are sent as a part of the websocket message
   */
  serializable_attributes: string[];

  constructor(event_id: string = undefined) {
    let constr: any = this.constructor; // As the this.event is static, it doesn't mix transparently with other class instance attributes
    this.event = constr.event;
    if (! this.event) { throw new Error(`Message '${constr}' is missing static attribute event!`) }

    this.event_id = event_id;
    if (! this.event_id) this.event_id = get_event_id(this.event)
  }
  construct(sender: string = undefined, recipient: string = undefined) {
    this.sender = sender;
    this.recipient = recipient;
  }
  validate_params(): void {
    this.serializable_attributes.forEach((attribute_name) => {
      if (!(this[attribute_name] || this[attribute_name] === 0)) {
        this.throw_missing_attribute(attribute_name)
      }
    });
  }

  static CreateClassInstance(raw_data: string, sender: string = undefined, recipient: string = undefined) {
    let data = JSON.parse(raw_data);
    let message: any = data.message;
    let event: string = data.event;
    let event_id: string = data.event_id;
    if (! event_id) { throw new Error(`Event '${raw_data}' is missing event_id!`) }

    let instance_data: [string, Object, string, string] = [event, message, sender, recipient];
    let instance: LEvent;
    if (event == 'ringtone-play')              { instance = new LERingtonePlay(message.ringtone_type, message.ringtone, sender, recipient, event_id) }
    else if (event == 'ringtone-played')       { instance = new LERingtonePlayed(message.ringtone_type, message.ringtone, sender, recipient, event_id) }
    else if (event === 'config-getpublic-response') { instance = new LEConfigGetpublic_Response(message.config, sender, recipient, event_id) }
    else if (event === 'config-getpublic')     { instance = new LEConfigGetpublic(sender, recipient, event_id) }
    else if (event === 'config-write')         { instance = new LEConfigWrite(message.variable, message.new_value, sender, recipient, event_id) }
    else if (event === 'rfid-tags-new')        { instance = new LERFIDTagsNew(message.tags_new, sender, recipient, event_id) }
    else if (event === 'rfid-tags-lost')       { instance = new LERFIDTagsLost(message.tags_lost, sender, recipient, event_id) }
    else if (event === 'rfid-tags-present')    { instance = new LERFIDTagsPresent(message.tags_present, sender, recipient, event_id) }
    else if (event === 'server-connected')     { instance = new LEServerConnected(event_id) }
    else if (event === 'server-disconnected')  { instance = new LEServerDisconnected(event_id) }
    else if (event === 'exception')            { instance = new LEException(message.exception, sender, recipient, event_id) }
    else {throw new Error(`Unknown event '${event}'`) }

    // Inject the raw data payload for debugging purposes
    if (raw_data) { instance.raw_data = raw_data }
    return instance;
  }

  serialize_for_ws(): string {
    let message = this.serializable_attributes.reduce(
      (attributes: any, attribute_name: string) => {
        attributes[attribute_name] = this[attribute_name];
        return attributes;
      }, {}
    )
    return JSON.stringify({
      'event': this.event,
      'message': message,
      'event_id': this.event_id,
    });
  }

  throw_missing_attribute(attribute_name): void {
    let class_name = this.constructor.name;
    throw new Error(`${class_name}():> Missing attribute '${attribute_name}'`);
  }
}

class LERingtonePlay extends LEvent {
  static event = 'ringtone-play';
  default_dispatch = 'server';

  serializable_attributes: any = ['ringtone_type', 'ringtone'];
  ringtone_type: string;
  ringtone: string;

  constructor(ringtone_type: string = undefined, ringtone: string = undefined, sender: string, recipient: string, event_id: string = undefined) {
    super(event_id);
    this.ringtone_type = ringtone_type;
    this.ringtone = ringtone;
    this.construct(sender, recipient);
    if (!(this.ringtone_type) && !(this.ringtone)) { this.throw_missing_attribute("ringtone_type' or 'ringtone'") }
  }
}
class LERingtonePlayed extends LEvent {
  static event = 'ringtone-played';

  serializable_attributes: any = ['ringtone_type', 'ringtone'];
  ringtone_type: string;
  ringtone: string;

  constructor(ringtone_type: string = undefined, ringtone: string = undefined, sender: string, recipient: string, event_id: string = undefined) {
    super(event_id);
    this.ringtone_type = ringtone_type;
    this.ringtone = ringtone;
    this.construct(sender, recipient);
    if (!(this.ringtone_type) && !(this.ringtone)) { this.throw_missing_attribute("ringtone_type' or 'ringtone'") }
  }
}
class LEConfigGetpublic extends LEvent {
  static event = 'config-getpublic';
  default_dispatch = 'server';

  constructor(sender: string, recipient: string, event_id: string = undefined) {
    super(event_id);
    this.construct(sender, recipient);
  }
}
class LEConfigGetpublic_Response extends LEvent {
  static event = 'config-getpublic-response';

  serializable_attributes: any = ['config'];
  config: any;

  constructor(config: any, sender: string, recipient: string, event_id: string = undefined) {
    super(event_id);
    this.config = config;
    this.construct(sender, recipient);
    this.validate_params();
  }
}
class LEConfigWrite extends LEvent {
  static event = 'config-write';
  default_dispatch = 'server';

  serializable_attributes: any = ['variable', 'new_value'];
  variable: string;
  new_value: string;

  constructor(variable: string, new_value:string, sender: string, recipient: string, event_id: string = undefined) {
    super(event_id);
    this.variable = variable;
    this.new_value = new_value;
    this.construct(sender, recipient);
    this.validate_params()
  }
}
class LERFIDTagsNew extends LEvent {
  static event = 'rfid-tags-new';

  serializable_attributes: any = ['tags_new'];
  tags_new: any;

  constructor(tags_new: any, sender: string, recipient: string, event_id: string = undefined) {
    super(event_id);
    this.tags_new = tags_new;
    this.construct(sender, recipient);
    this.validate_params()
  }
}
class LERFIDTagsLost extends LEvent {
  static event = 'rfid-tags-lost';

  serializable_attributes: any = ['tags_lost'];
  tags_lost: any;

  constructor(tags_lost: any, sender: string, recipient: string, event_id: string = undefined) {
    super(event_id);
    this.tags_lost = tags_lost;
    this.construct(sender, recipient);
    this.validate_params()
  }
}
class LERFIDTagsPresent extends LEvent {
  static event = 'rfid-tags-present';

  serializable_attributes: any = ['tags_present'];
  tags_present: any;

  constructor(tags_present: any, sender: string, recipient: string, event_id: string = undefined) {
    super(event_id);
    this.tags_present = tags_present;
    this.construct(sender, recipient);
    this.validate_params()
  }
}
class LEServerConnected extends LEvent {
  static event = 'server-connected';

  constructor(event_id: string = undefined) {
    super(event_id);
  }
}
class LEServerDisconnected extends LEvent {
  static event = 'server-disconnected';

  constructor(event_id: string = undefined) {
    super(event_id);
  }
}
class LEException extends LEvent {
  static event = 'exception';

  serializable_attributes: any = ['exception'];
  exception: string;
  e: Error;

  constructor(e: Error | string, sender: string, recipient: string, event_id: string = undefined) {
    super(event_id);
    if (e instanceof Error) {
      this.e = e;
      this.exception = e.message + "\n" + e.stack;
    }
    else {
      this.exception = e;
    }
    this.construct(sender, recipient);
    this.validate_params()
  }
}

let event_id: number = 0;
function get_event_id(event_name: string): string {
  return event_name + '-' + event_id++;
}

class Lainuri {

  base_url: string;
  ws: WebSocket;
  config: any;
  listeners: Map<Function, Function> = new Map();

  constructor(base_url: string = 'ws://localhost:53153') {
    this.base_url = base_url;

    // The connected websocket immediately responds with configuration and inventory status
    // So we need to define the listeners in advance
    this.attach_event_listener(LEConfigGetpublic_Response, (event: LEConfigGetpublic_Response) => {
      this.config = event.config;
      console.log(`Received new configurations():> '${event.config}'`, event);
    });
  }

  open_websocket_connection(): WebSocket {
    this.ws = new WebSocket(this.base_url);
    this.ws.onopen = (event) => {
      try {
        this.dispatch_event(new LEServerConnected());
      }
      catch(e) {
        console.error(e)
        this.dispatch_event(new LEException(e, 'client', 'server'));
      }
    }
    this.ws.onclose = (event) => {
      try {
        this.dispatch_event(new LEServerDisconnected());
      }
      catch(e) {
        this.dispatch_event(new LEException(e, 'client', 'server'));
      }
    }
    this.ws.onmessage = (event) => {
      try {
        console.log("Lainuri - ws.onmessage()", event);
        this.dispatch_event(LEvent.CreateClassInstance(event.data, 'server', 'client'));
      }
      catch(e) {
        this.dispatch_event(new LEException(e, 'client', 'server'));
      }
    }
    this.ws.onerror = (event: any) => {
      console.error(event);
      this.dispatch_event(new LEException(new Error(event.data), 'client', 'server'))
    }
    return this.ws;
  }

  attach_event_listener(event_class: any, event_handler: Function): this {
    console.log(`Registering new event listener for event '${event_class.event}'`);
    if (! this.listeners[event_class.event]) { this.listeners[event_class.event] = [] }
    this.listeners[event_class.event].push(event_handler);
    return this;
  }

  dispatch_event(event: LEvent): void {
    let dispatched_times = 0
    if (this.listeners[event.event]) {
      this.listeners[event.event].forEach(listener => {
        dispatched_times++;
        listener(event);
      });
    }
    if (event.recipient === 'server' || event.default_dispatch === 'server') {
      dispatched_times++;
      let payload = event.serialize_for_ws();
      console.log(`dispatch_event():> Sending '${payload}'`)
      this.ws.send(payload);
    }
    if (! dispatched_times) {
      throw new Error(`Dispatching event '${event.event}', but no event handler registered?`);
    }
  }
}
