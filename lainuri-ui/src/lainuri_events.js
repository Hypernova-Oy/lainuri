'use strict';

let event_id = 0;
function get_event_id(event_name) {
  return event_name + '-' + event_id++;
}

class LEvent {

  event
  message;
  raw_data;
  sender;
  recipient;
  default_dispatch = undefined;
  event_id;

  /**
   * Overload. These attributes are sent as a part of the websocket message
   */
  static serializable_attributes = [];

  lifecycle_hooks = ['ondispatched', 'onsuccess', 'onerror'];
  lifecycle_hook_impls = {};
  lifecycle_map_event_to_hooks = []

  constructor(event_id = undefined) {
    let constr = this.constructor; // As the this.event is static, it doesn't mix transparently with other class instance attributes
    this.event = constr.event;
    if (! this.event) { throw new Error(`Message '${constr}' is missing static attribute event!`) }

    this.event_id = event_id;
    if (! this.event_id) this.event_id = get_event_id(this.event)
  }
  construct(sender = undefined, recipient = undefined) {
    this.sender = sender;
    this.recipient = recipient;
  }
  validate_params() {
    this.constructor.serializable_attributes.forEach((attribute_name) => {
      if (!(this[attribute_name] || this[attribute_name] === 0)) {
        this.throw_missing_attribute(attribute_name)
      }
    });
  }

  on(lifecycle_phase, cb) {
    if (lifecycle_phase && !this.lifecycle_hooks[lifecycle_phase]) {
      throw new Error(`Lifecycle phase '${lifecycle_phase}' not supported by event '${this.constructor.name}'`);
    }
    if (! this.lifecycle_hook_impls[lifecycle_phase]) {
      this.lifecycle_hook_impls[lifecycle_phase] = [];
    }
    this.lifecycle_hook_impls[this.lifecycle_hooks].append(cb);
  }
  lifecycle_reached(lifecycle_phase) {
    if (lifecycle_phase instanceof LEvent) {
      lifecycle_phase = this.lifecycle_map_event_to_hooks[lifecycle_phase.event];
      if (!lifecycle_phase) { throw new Error(`LEvent '${this.constructor.name}' is missing lifecycle phase transition from LEvent '${lifecycle_phase.constructor.name}'`); }
    }
    if (typeof lifecycle_phase === "string") {
      if (this.lifecycle_hook_impls[lifecycle_phase]) {
        console.log(`Calling lifecycle hooks '${lifecycle_phase}' of '${this.constructor.name}'`);
        this.lifecycle_hook_impls[lifecycle_phase].forEach((cb) => cb.call(this));
      }
    }
  }

  serialize_for_ws() {
    let message = this.constructor.serializable_attributes.reduce(
      (attributes, attribute_name) => {
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

  throw_missing_attribute(attribute_name) {
    let class_name = this.constructor.name;
    throw new Error(`${class_name}():> Missing attribute '${attribute_name}'`);
  }
}

class LEBarcodeRead extends LEvent {
  static event = 'barcode-read';

  static serializable_attributes = ['barcode'];
  barcode;

  constructor(barcode = undefined, sender, recipient, event_id = undefined) {
    super(event_id);
    this.barcode = barcode;
    this.construct(sender, recipient);
    this.validate_params();
  }
}
class LERingtonePlay extends LEvent {
  static event = 'ringtone-play';
  default_dispatch = 'server';

  static serializable_attributes = ['ringtone_type', 'ringtone'];
  ringtone_type;
  ringtone;

  constructor(ringtone_type = undefined, ringtone = undefined, sender, recipient, event_id = undefined) {
    super(event_id);
    this.ringtone_type = ringtone_type;
    this.ringtone = ringtone;
    this.construct(sender, recipient);
    if (!(this.ringtone_type) && !(this.ringtone)) { this.throw_missing_attribute("ringtone_type' or 'ringtone'") }
  }
}
class LERingtonePlayed extends LEvent {
  static event = 'ringtone-played';

  static serializable_attributes = ['ringtone_type', 'ringtone'];
  ringtone_type;
  ringtone;

  constructor(ringtone_type = undefined, ringtone = undefined, sender, recipient, event_id = undefined) {
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

  constructor(sender, recipient, event_id = undefined) {
    super(event_id);
    this.construct(sender, recipient);
  }
}
class LEConfigGetpublic_Response extends LEvent {
  static event = 'config-getpublic-response';

  static serializable_attributes = ['config'];
  config;

  constructor(config, sender, recipient, event_id = undefined) {
    super(event_id);
    this.config = config;
    this.construct(sender, recipient);
    this.validate_params();
  }
}
class LEConfigWrite extends LEvent {
  static event = 'config-write';
  default_dispatch = 'server';

  static serializable_attributes = ['variable', 'new_value'];
  variable;
  new_value;

  constructor(variable, new_value, sender, recipient, event_id = undefined) {
    super(event_id);
    this.variable = variable;
    this.new_value = new_value;
    this.construct(sender, recipient);
    this.validate_params()
  }
}
class LERFIDTagsNew extends LEvent {
  static event = 'rfid-tags-new';

  static serializable_attributes = ['tags_new','tags_present'];
  tags_new;
  tags_present;

  constructor(tags_new, tags_present, sender, recipient, event_id = undefined) {
    super(event_id);
    this.tags_new = tags_new;
    this.tags_present = tags_present;
    this.construct(sender, recipient);
    this.validate_params()
  }
}
class LERFIDTagsLost extends LEvent {
  static event = 'rfid-tags-lost';

  static serializable_attributes = ['tags_lost','tags_present'];
  tags_lost;
  tags_present;

  constructor(tags_lost, tags_present, sender, recipient, event_id = undefined) {
    super(event_id);
    this.tags_lost = tags_lost;
    this.tags_present = tags_present;
    this.construct(sender, recipient);
    this.validate_params()
  }
}
class LERFIDTagsPresent extends LEvent {
  static event = 'rfid-tags-present';

  static serializable_attributes = ['tags_present'];
  tags_present;

  constructor(tags_present, sender, recipient, event_id = undefined) {
    super(event_id);
    this.tags_present = tags_present;
    this.construct(sender, recipient);
    this.validate_params()
  }
}
class LEServerConnected extends LEvent {
  static event = 'server-connected';

  constructor(event_id = undefined) {
    super(event_id);
  }
}
class LEServerDisconnected extends LEvent {
  static event = 'server-disconnected';

  constructor(event_id = undefined) {
    super(event_id);
  }
}
class LEUserLoggingIn extends LEvent {
  static event = 'user-logging-in';
  default_dispatch = 'server';

  static serializable_attributes = ['username, password'];
  username;
  password;

  lifecycle_map_event_to_hooks = {
    [LEUserLoggedIn.constructor.name]: 'onsuccess',
    [LEException.constructor.name]: 'onerror',
  };

  constructor(username = '', password = '', sender, recipient, event_id = undefined) {
    super(event_id);
    this.username = username;
    this.password = password;
    this.construct(sender, recipient);
    //this.validate_params()
  }
}
class LEUserLoggedIn extends LEvent {
  static event = 'user-logged-in';

  static serializable_attributes = ['firstname', 'surname', 'cardnumber'];
  firstname;
  surname;
  cardnumber;
  password;

  lifecycle_map_event_to_hooks = {
    [LEUserLoggedIn.constructor.name]: 'onsuccess',
    [LEException.constructor.name]: 'onerror',
  };

  constructor(firstname, surname, cardnumber, sender, recipient, event_id = undefined) {
    super(event_id);
    this.firstname = firstname;
    this.surname = surname;
    this.cardnumber = cardnumber;
    this.construct(sender, recipient);
    this.validate_params()
  }
}
class LEUserLoginAbort extends LEvent {
  static event = 'user-login-abort';
  default_dispatch = 'server';

  constructor(sender, recipient, event_id = undefined) {
    super(event_id);
    this.construct(sender, recipient);
  }
}
class LEException extends LEvent {
  static event = 'exception';

  static serializable_attributes = ['exception'];
  exception;
  e;

  constructor(e, sender, recipient, event_id = undefined) {
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

  static serializable_attributes = [];

  constructor(event_id = undefined) {
    super(event_id);
  }
}

export {
  LEvent, LEException, LEBarcodeRead, LEConfigWrite, LEConfigGetpublic, LEConfigGetpublic_Response, LERFIDTagsLost, LERFIDTagsNew, LERFIDTagsPresent, LERingtonePlay, LERingtonePlayed, LEServerConnected, LEServerDisconnected, LETestMockDevices, LEUserLoggedIn, LEUserLoggingIn, LEUserLoginAbort, LEUserLoginFailed
}
