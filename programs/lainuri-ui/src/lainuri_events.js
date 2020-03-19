'use strict';

let event_id = 0;
function get_event_id(event_name) {
  return event_name + '-' + event_id++;
}

const Status = Object.freeze({
  "SUCCESS":"SUCCESS",
  "ERROR":"ERROR",
  "PENDING":"PENDING",
  "NOT_SET":"NOT_SET",
})

class LEvent {

  event
  message;
  raw_data;
  sender;
  recipient;
  default_dispatch = undefined;
  event_id;

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
      if (!(this[attribute_name]) && (this[attribute_name] === undefined || this[attribute_name] === null)) {
        this.throw_missing_attribute(attribute_name)
      }
    });
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

class LECheckOut extends LEvent {
  static event = 'check-out';

  static serializable_attributes = ['item_barcode', 'user_barcode', 'tag_type'];
  item_barcode;
  user_barcode;
  tag_type;

  constructor(item_barcode, user_barcode, tag_type = 'rfid', sender, recipient, event_id = undefined) {
    super(event_id);
    this.item_barcode = item_barcode;
    this.user_barcode = user_barcode;
    this.tag_type = tag_type;
    this.construct(sender, recipient);
    this.validate_params();
  }
}

class LECheckOutComplete extends LEvent {
  static event = 'check-out-complete';

  static serializable_attributes = ['item_barcode', 'user_barcode', 'tag_type', 'status', 'states'];
  item_barcode;
  user_barcode;
  tag_type;
  states;
  status = Status.NOT_SET;

  constructor(item_barcode, user_barcode, tag_type = 'rfid', status, states, sender, recipient, event_id = undefined) {
    super(event_id);
    this.item_barcode = item_barcode
    this.user_barcode = user_barcode
    this.tag_type = tag_type
    this.states = states
    this.status = status
    this.construct(sender, recipient);
    this.validate_params();
  }
}

class LECheckIn extends LEvent {
  static event = 'check-in';

  static serializable_attributes = ['item_barcode', 'tag_type'];
  item_barcode;
  tag_type;

  constructor(item_barcode, tag_type = 'rfid', sender, recipient, event_id = undefined) {
    super(event_id);
    this.item_barcode = item_barcode;
    this.tag_type = tag_type;
    this.construct(sender, recipient);
    this.validate_params();
  }
}

class LECheckInComplete extends LEvent {
  static event = 'check-in-complete';

  static serializable_attributes = ['item_barcode', 'tag_type', 'status', 'states'];
  item_barcode;
  tag_type;
  states;
  status = Status.NOT_SET;

  constructor(item_barcode, tag_type = 'rfid', status, states, sender, recipient, event_id = undefined) {
    super(event_id);
    this.item_barcode = item_barcode
    this.tag_type = tag_type;
    this.states = states
    this.status = status
    this.construct(sender, recipient);
    this.validate_params();
  }
}

class LELocaleSet extends LEvent {
  static event = 'locale-set'
  default_dispatch = 'server'

  static serializable_attributes = ['locale_code']
  locale_code;

  constructor(locale_code, sender, recipient, event_id = undefined) {
    super(event_id);
    this.locale_code = locale_code
    this.construct(sender, recipient);
    this.validate_params()
  }
}

class LESetTagAlarm extends LEvent {
  static event = 'set-tag-alarm';

  static serializable_attributes = ['item_barcode', 'on'];
  item_barcode;
  on;

  constructor(item_barcode, on, sender, recipient, event_id) {
    super(event_id)
    this.item_barcode = item_barcode
    this.on = on
    this.construct(sender, recipient);
    this.validate_params();
  }
}

class LESetTagAlarmComplete extends LEvent {
  static event = 'set-tag-alarm-complete'

  static serializable_attributes = ['item_barcode', 'on', 'status', 'states']
  item_barcode;
  on;
  states;
  status = Status.NOT_SET;

  constructor(item_barcode, on, status, states, sender, recipient, event_id) {
    super(event_id)
    this.item_barcode = item_barcode
    this.on = on
    this.states = states
    this.status = status
    this.construct(sender, recipient);
    this.validate_params();
  }
}

class LEBarcodeRead extends LEvent {
  static event = 'barcode-read';

  static serializable_attributes = ['barcode', 'tag'];
  barcode;
  tag;

  constructor(barcode, tag, sender, recipient, event_id = undefined) {
    super(event_id);
    this.barcode = barcode;
    this.tag = tag;
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
class LERingtonePlayComplete extends LEvent {
  static event = 'ringtone-play-complete';

  static serializable_attributes = ['status', 'ringtone_type', 'ringtone', 'states'];
  ringtone_type;
  ringtone;
  states;
  status = Status.NOT_SET;

  constructor(status, ringtone_type = undefined, ringtone = undefined, states, sender, recipient, event_id = undefined) {
    super(event_id);
    this.ringtone_type = ringtone_type;
    this.ringtone = ringtone;
    this.states = states
    this.status = status
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
class LELogSend extends LEvent {
  static event = 'log-send'
  default_dispatch = 'server'

  static serializable_attributes = ['level', 'logger_name', 'milliseconds', 'log_entry']
  level;
  logger_name;
  milliseconds;
  log_entry;

  constructor(level, logger_name, milliseconds, log_entry, sender, recipient, event_id = undefined) {
    super(event_id);
    this.level = level;
    this.logger_name = logger_name;
    this.milliseconds = milliseconds;
    this.log_entry = log_entry;
    this.construct(sender, recipient);
    this.validate_params();
  }
}
class LELogReceived extends LEvent {
  static event = 'log-received'

  static serializable_attributes = ['status', 'states']
  states;
  status = Status.NOT_SET

  constructor(status, states, sender, recipient, event_id = undefined) {
    super(event_id);
    this.states = states
    this.status = status
    this.construct(sender, recipient);
    this.validate_params()
  }
}
class LEPrintRequest extends LEvent {
  static event = 'print-request'
  default_dispatch = 'server'

  static serializable_attributes = ['receipt_type', 'items', 'user_barcode']
  receipt_type;
  items;
  user_barcode;

  constructor(receipt_type, items, user_barcode, sender, recipient, event_id = undefined) {
    super(event_id);
    this.receipt_type = receipt_type;
    this.items = items
    this.user_barcode = user_barcode
    this.construct(sender, recipient);
    this.validate_params()
  }
}
class LEPrintResponse extends LEvent {
  static event = 'print-response'

  static serializable_attributes = ['receipt_type', 'items', 'user_barcode', 'printable_sheet', 'status', 'states']
  receipt_type;
  items;
  user_barcode;
  printable_sheet;
  states;
  status = Status.NOT_SET

  constructor(receipt_type, items, user_barcode, printable_sheet, status, states, sender, recipient, event_id = undefined) {
    super(event_id);
    this.receipt_type = receipt_type
    this.items = items
    this.user_barcode = user_barcode
    this.printable_sheet = printable_sheet
    this.states = states
    this.status = status
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
class LERFIDTagsPresentRequest extends LEvent {
  static event = 'rfid-tags-present-request';
  default_dispatch = 'server';

  static serializable_attributes = [];

  constructor(sender, recipient, event_id = undefined) {
    super(event_id);
    this.construct(sender, recipient);
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
class LEServerStatusRequest extends LEvent {
  static event = 'server-status-request';
  default_dispatch = 'server';

  static serializable_attributes = [];

  constructor(sender, recipient, event_id = undefined) {
    super(event_id);
    this.construct(sender, recipient);
  }
}

class LEServerStatusResponse extends LEvent {
  static event = 'server-status-response';

  static serializable_attributes = ['barcode_reader_status', 'thermal_printer_status', 'rfid_reader_status', 'touch_screen_status', 'ils_connection_status'];
  barcode_reader_status;
  thermal_printer_status;
  rfid_reader_status;
  touch_screen_status;
  ils_connection_status;

  constructor(barcode_reader_status, thermal_printer_status, rfid_reader_status, touch_screen_status, ils_connection_status, sender, recipient, event_id = undefined) {
    super(event_id);
    this.barcode_reader_status = barcode_reader_status
    this.thermal_printer_status = thermal_printer_status
    this.rfid_reader_status = rfid_reader_status
    this.touch_screen_status = touch_screen_status
    this.ils_connection_status = ils_connection_status
    this.construct(sender, recipient);
    this.validate_params()
  }
}

class LEUserLoggingIn extends LEvent {
  static event = 'user-logging-in';
  default_dispatch = 'server';

  static serializable_attributes = ['username, password'];
  username;
  password;

  constructor(username = '', password = '', sender, recipient, event_id = undefined) {
    super(event_id);
    this.username = username;
    this.password = password;
    this.construct(sender, recipient);
    //this.validate_params()
  }
}
class LEUserLoginComplete extends LEvent {
  static event = 'user-login-complete';

  static serializable_attributes = ['firstname', 'surname', 'user_barcode', 'status', 'states'];
  firstname;
  surname;
  user_barcode;
  password;
  states;
  status = Status.NOT_SET;

  constructor(firstname, surname, user_barcode, status, states, sender, recipient, event_id = undefined) {
    super(event_id);
    this.firstname = firstname;
    this.surname = surname;
    this.user_barcode = user_barcode;
    this.states = states
    this.status = status
    this.construct(sender, recipient);
    this.validate_params()
  }
}
class LEUserLoginAbort extends LEvent {
  static event = 'user-login-abort';
  default_dispatch = 'server';

  static serializable_attributes = [];

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
  Status, LEvent, LEException, LEBarcodeRead, LECheckIn, LECheckInComplete, LELogSend, LELogReceived, LELocaleSet, LESetTagAlarm, LESetTagAlarmComplete, LECheckOut, LECheckOutComplete, LEConfigWrite, LEConfigGetpublic, LEConfigGetpublic_Response, LEPrintRequest, LEPrintResponse, LERFIDTagsLost, LERFIDTagsNew, LERFIDTagsPresentRequest, LERFIDTagsPresent, LERingtonePlay, LERingtonePlayComplete, LEServerConnected, LEServerDisconnected, LEServerStatusRequest, LEServerStatusResponse, LETestMockDevices, LEUserLoginComplete, LEUserLoggingIn, LEUserLoginAbort
}
