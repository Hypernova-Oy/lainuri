'use strict';

let event_id: number = 0;
function get_event_id(event_name: string): string {
  return event_name + '-' + event_id++;
}

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

  lifecycle_hooks: any = ['ondispatched', 'onsuccess', 'onerror'];
  lifecycle_hook_impls: Map<String, Function> = <Map<String, Function>>{};
  lifecycle_map_event_to_hooks: any = []

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

  on(lifecycle_phase: string, cb: Function): any {
    if (lifecycle_phase && !this.lifecycle_hooks[lifecycle_phase]) {
      throw new Error(`Lifecycle phase '${lifecycle_phase}' not supported by event '${this.constructor.name}'`);
    }
    if (! this.lifecycle_hook_impls[lifecycle_phase]) {
      this.lifecycle_hook_impls[lifecycle_phase] = [];
    }
    this.lifecycle_hook_impls[this.lifecycle_hooks].append(cb);
  }
  lifecycle_reached(lifecycle_phase: string|LEvent): void {
    if (lifecycle_phase instanceof LEvent) {
      lifecycle_phase = this.lifecycle_map_event_to_hooks[lifecycle_phase.event];
      if (!lifecycle_phase) { throw new Error(`LEvent '${this.constructor.name}' is missing lifecycle phase transition from LEvent '${lifecycle_phase.constructor.name}'`); }
    }
    if (typeof lifecycle_phase === "string") {
      if (this.lifecycle_hook_impls[lifecycle_phase]) {
        console.log(`Calling lifecycle hooks '${lifecycle_phase}' of '${this.constructor.name}'`);
        this.lifecycle_hook_impls[lifecycle_phase].forEach((cb: Function) => cb.call(this));
      }
    }
  }

  static CreateClassInstance(raw_data: string, sender: string = undefined, recipient: string = undefined) {
    let data = JSON.parse(raw_data);
    let message: any = data.message;
    let event: string = data.event;
    let event_id: string = data.event_id;
    if (! event_id) { throw new Error(`Event '${raw_data}' is missing event_id!`) }

    let instance_data: [string, Object, string, string] = [event, message, sender, recipient];
    let instance: LEvent;
    if (event == 'barcode-read')               { instance = new LEBarcodeRead(message.barcode, sender, recipient, event_id) }
    else if (event == 'ringtone-play')         { instance = new LERingtonePlay(message.ringtone_type, message.ringtone, sender, recipient, event_id) }
    else if (event == 'ringtone-played')       { instance = new LERingtonePlayed(message.ringtone_type, message.ringtone, sender, recipient, event_id) }
    else if (event === 'config-getpublic-response') { instance = new LEConfigGetpublic_Response(message.config, sender, recipient, event_id) }
    else if (event === 'config-getpublic')     { instance = new LEConfigGetpublic(sender, recipient, event_id) }
    else if (event === 'config-write')         { instance = new LEConfigWrite(message.variable, message.new_value, sender, recipient, event_id) }
    else if (event === 'rfid-tags-new')        { instance = new LERFIDTagsNew(message.tags_new, message.tags_present, sender, recipient, event_id) }
    else if (event === 'rfid-tags-lost')       { instance = new LERFIDTagsLost(message.tags_lost, message.tags_present, sender, recipient, event_id) }
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

class LEBarcodeRead extends LEvent {
  static event = 'barcode-read';

  serializable_attributes: any = ['barcode'];
  barcode: string;

  constructor(barcode: string = undefined, sender: string, recipient: string, event_id: string = undefined) {
    super(event_id);
    this.barcode = barcode;
    this.construct(sender, recipient);
    this.validate_params();
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

  serializable_attributes: any = ['tags_new','tags_present'];
  tags_new: any;
  tags_present: any;

  constructor(tags_new: any, tags_present: any, sender: string, recipient: string, event_id: string = undefined) {
    super(event_id);
    this.tags_new = tags_new;
    this.tags_present = tags_present;
    this.construct(sender, recipient);
    this.validate_params()
  }
}
class LERFIDTagsLost extends LEvent {
  static event = 'rfid-tags-lost';

  serializable_attributes: any = ['tags_lost','tags_present'];
  tags_lost: any;
  tags_present: any;

  constructor(tags_lost: any, tags_present: any, sender: string, recipient: string, event_id: string = undefined) {
    super(event_id);
    this.tags_lost = tags_lost;
    this.tags_present = tags_present;
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
class LEUserLoggingIn extends LEvent {
  static event = 'user-logging-in';

  serializable_attributes: any = ['username, password'];
  username: string;
  password: string;

  lifecycle_map_event_to_hooks: any = {
    [LEUserLoggedIn.constructor.name]: 'onsuccess',
    [LEException.constructor.name]: 'onerror',
  };

  constructor(username: string = '', password: string = '', sender: string, recipient: string, event_id: string = undefined) {
    super(event_id);
    this.username = username;
    this.password = password;
    this.construct(sender, recipient);
    this.validate_params()
  }
}
class LEUserLoggedIn extends LEvent {
  static event = 'user-logged-in';

  serializable_attributes: any = ['firstname, surname, cardnumber, password'];
  firstname: string;
  surname: string;
  cardnumber: string;
  password: string;

  lifecycle_map_event_to_hooks: any = {
    [LEUserLoggedIn.constructor.name]: 'onsuccess',
    [LEException.constructor.name]: 'onerror',
  };

  constructor(firstname: string, surname: string, cardnumber: string, password: string, sender: string, recipient: string, event_id: string = undefined) {
    super(event_id);
    this.firstname = firstname;
    this.surname = surname;
    this.cardnumber = cardnumber;
    this.password = password;
    this.construct(sender, recipient);
    this.validate_params()
  }
}
class LEUserLoginAbort extends LEvent {
  static event = 'user-login-abort';

  constructor(sender: string, recipient: string, event_id: string = undefined) {
    super(event_id);
    this.construct(sender, recipient);
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
class LEUserLoginFailed extends LEException {
  static event = 'user-login-failed';
}
/**
 * Trigger the server to send mocked RFID tag reads and barcode reads
 */
class LETestMockDevices extends LEvent {
  static event = 'test-mock-devices';
  default_dispatch = 'server';

  serializable_attributes: any = [];

  constructor(event_id: string = undefined) {
    super(event_id);
  }
}

export {
  LEvent, LEException, LEConfigWrite, LEConfigGetpublic, LEConfigGetpublic_Response, LERFIDTagsLost, LERFIDTagsNew, LERFIDTagsPresent, LERingtonePlay, LERingtonePlayed, LEServerConnected, LEServerDisconnected, LETestMockDevices, LEUserLoggedIn, LEUserLoggingIn, LEUserLoginAbort, LEUserLoginFailed
}
