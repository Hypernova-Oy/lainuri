'use strict';
Object.defineProperty(exports, "__esModule", { value: true });
let event_id = 0;
function get_event_id(event_name) {
    return event_name + '-' + event_id++;
}
class LEvent {
    constructor(event_id = undefined) {
        this.default_dispatch = undefined;
        this.lifecycle_hooks = ['ondispatched', 'onsuccess', 'onerror'];
        this.lifecycle_hook_impls = {};
        this.lifecycle_map_event_to_hooks = [];
        let constr = this.constructor; // As the this.event is static, it doesn't mix transparently with other class instance attributes
        this.event = constr.event;
        if (!this.event) {
            throw new Error(`Message '${constr}' is missing static attribute event!`);
        }
        this.event_id = event_id;
        if (!this.event_id)
            this.event_id = get_event_id(this.event);
    }
    construct(sender = undefined, recipient = undefined) {
        this.sender = sender;
        this.recipient = recipient;
    }
    validate_params() {
        this.serializable_attributes.forEach((attribute_name) => {
            if (!(this[attribute_name] || this[attribute_name] === 0)) {
                this.throw_missing_attribute(attribute_name);
            }
        });
    }
    on(lifecycle_phase, cb) {
        if (lifecycle_phase && !this.lifecycle_hooks[lifecycle_phase]) {
            throw new Error(`Lifecycle phase '${lifecycle_phase}' not supported by event '${this.constructor.name}'`);
        }
        if (!this.lifecycle_hook_impls[lifecycle_phase]) {
            this.lifecycle_hook_impls[lifecycle_phase] = [];
        }
        this.lifecycle_hook_impls[this.lifecycle_hooks].append(cb);
    }
    lifecycle_reached(lifecycle_phase) {
        if (lifecycle_phase instanceof LEvent) {
            lifecycle_phase = this.lifecycle_map_event_to_hooks[lifecycle_phase.event];
            if (!lifecycle_phase) {
                throw new Error(`LEvent '${this.constructor.name}' is missing lifecycle phase transition from LEvent '${lifecycle_phase.constructor.name}'`);
            }
        }
        if (typeof lifecycle_phase === "string") {
            if (this.lifecycle_hook_impls[lifecycle_phase]) {
                console.log(`Calling lifecycle hooks '${lifecycle_phase}' of '${this.constructor.name}'`);
                this.lifecycle_hook_impls[lifecycle_phase].forEach((cb) => cb.call(this));
            }
        }
    }
    static CreateClassInstance(raw_data, sender = undefined, recipient = undefined) {
        let data = JSON.parse(raw_data);
        let message = data.message;
        let event = data.event;
        let event_id = data.event_id;
        if (!event_id) {
            throw new Error(`Event '${raw_data}' is missing event_id!`);
        }
        let instance_data = [event, message, sender, recipient];
        let instance;
        if (event == 'barcode-read') {
            instance = new LEBarcodeRead(message.barcode, sender, recipient, event_id);
        }
        else if (event == 'ringtone-play') {
            instance = new LERingtonePlay(message.ringtone_type, message.ringtone, sender, recipient, event_id);
        }
        else if (event == 'ringtone-played') {
            instance = new LERingtonePlayed(message.ringtone_type, message.ringtone, sender, recipient, event_id);
        }
        else if (event === 'config-getpublic-response') {
            instance = new LEConfigGetpublic_Response(message.config, sender, recipient, event_id);
        }
        else if (event === 'config-getpublic') {
            instance = new LEConfigGetpublic(sender, recipient, event_id);
        }
        else if (event === 'config-write') {
            instance = new LEConfigWrite(message.variable, message.new_value, sender, recipient, event_id);
        }
        else if (event === 'rfid-tags-new') {
            instance = new LERFIDTagsNew(message.tags_new, message.tags_present, sender, recipient, event_id);
        }
        else if (event === 'rfid-tags-lost') {
            instance = new LERFIDTagsLost(message.tags_lost, message.tags_present, sender, recipient, event_id);
        }
        else if (event === 'rfid-tags-present') {
            instance = new LERFIDTagsPresent(message.tags_present, sender, recipient, event_id);
        }
        else if (event === 'server-connected') {
            instance = new LEServerConnected(event_id);
        }
        else if (event === 'server-disconnected') {
            instance = new LEServerDisconnected(event_id);
        }
        else if (event === 'exception') {
            instance = new LEException(message.exception, sender, recipient, event_id);
        }
        else {
            throw new Error(`Unknown event '${event}'`);
        }
        // Inject the raw data payload for debugging purposes
        if (raw_data) {
            instance.raw_data = raw_data;
        }
        return instance;
    }
    serialize_for_ws() {
        let message = this.serializable_attributes.reduce((attributes, attribute_name) => {
            attributes[attribute_name] = this[attribute_name];
            return attributes;
        }, {});
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
exports.LEvent = LEvent;
class LEBarcodeRead extends LEvent {
    constructor(barcode = undefined, sender, recipient, event_id = undefined) {
        super(event_id);
        this.serializable_attributes = ['barcode'];
        this.barcode = barcode;
        this.construct(sender, recipient);
        this.validate_params();
    }
}
LEBarcodeRead.event = 'barcode-read';
class LERingtonePlay extends LEvent {
    constructor(ringtone_type = undefined, ringtone = undefined, sender, recipient, event_id = undefined) {
        super(event_id);
        this.default_dispatch = 'server';
        this.serializable_attributes = ['ringtone_type', 'ringtone'];
        this.ringtone_type = ringtone_type;
        this.ringtone = ringtone;
        this.construct(sender, recipient);
        if (!(this.ringtone_type) && !(this.ringtone)) {
            this.throw_missing_attribute("ringtone_type' or 'ringtone'");
        }
    }
}
exports.LERingtonePlay = LERingtonePlay;
LERingtonePlay.event = 'ringtone-play';
class LERingtonePlayed extends LEvent {
    constructor(ringtone_type = undefined, ringtone = undefined, sender, recipient, event_id = undefined) {
        super(event_id);
        this.serializable_attributes = ['ringtone_type', 'ringtone'];
        this.ringtone_type = ringtone_type;
        this.ringtone = ringtone;
        this.construct(sender, recipient);
        if (!(this.ringtone_type) && !(this.ringtone)) {
            this.throw_missing_attribute("ringtone_type' or 'ringtone'");
        }
    }
}
exports.LERingtonePlayed = LERingtonePlayed;
LERingtonePlayed.event = 'ringtone-played';
class LEConfigGetpublic extends LEvent {
    constructor(sender, recipient, event_id = undefined) {
        super(event_id);
        this.default_dispatch = 'server';
        this.construct(sender, recipient);
    }
}
exports.LEConfigGetpublic = LEConfigGetpublic;
LEConfigGetpublic.event = 'config-getpublic';
class LEConfigGetpublic_Response extends LEvent {
    constructor(config, sender, recipient, event_id = undefined) {
        super(event_id);
        this.serializable_attributes = ['config'];
        this.config = config;
        this.construct(sender, recipient);
        this.validate_params();
    }
}
exports.LEConfigGetpublic_Response = LEConfigGetpublic_Response;
LEConfigGetpublic_Response.event = 'config-getpublic-response';
class LEConfigWrite extends LEvent {
    constructor(variable, new_value, sender, recipient, event_id = undefined) {
        super(event_id);
        this.default_dispatch = 'server';
        this.serializable_attributes = ['variable', 'new_value'];
        this.variable = variable;
        this.new_value = new_value;
        this.construct(sender, recipient);
        this.validate_params();
    }
}
exports.LEConfigWrite = LEConfigWrite;
LEConfigWrite.event = 'config-write';
class LERFIDTagsNew extends LEvent {
    constructor(tags_new, tags_present, sender, recipient, event_id = undefined) {
        super(event_id);
        this.serializable_attributes = ['tags_new', 'tags_present'];
        this.tags_new = tags_new;
        this.tags_present = tags_present;
        this.construct(sender, recipient);
        this.validate_params();
    }
}
exports.LERFIDTagsNew = LERFIDTagsNew;
LERFIDTagsNew.event = 'rfid-tags-new';
class LERFIDTagsLost extends LEvent {
    constructor(tags_lost, tags_present, sender, recipient, event_id = undefined) {
        super(event_id);
        this.serializable_attributes = ['tags_lost', 'tags_present'];
        this.tags_lost = tags_lost;
        this.tags_present = tags_present;
        this.construct(sender, recipient);
        this.validate_params();
    }
}
exports.LERFIDTagsLost = LERFIDTagsLost;
LERFIDTagsLost.event = 'rfid-tags-lost';
class LERFIDTagsPresent extends LEvent {
    constructor(tags_present, sender, recipient, event_id = undefined) {
        super(event_id);
        this.serializable_attributes = ['tags_present'];
        this.tags_present = tags_present;
        this.construct(sender, recipient);
        this.validate_params();
    }
}
exports.LERFIDTagsPresent = LERFIDTagsPresent;
LERFIDTagsPresent.event = 'rfid-tags-present';
class LEServerConnected extends LEvent {
    constructor(event_id = undefined) {
        super(event_id);
    }
}
exports.LEServerConnected = LEServerConnected;
LEServerConnected.event = 'server-connected';
class LEServerDisconnected extends LEvent {
    constructor(event_id = undefined) {
        super(event_id);
    }
}
exports.LEServerDisconnected = LEServerDisconnected;
LEServerDisconnected.event = 'server-disconnected';
class LEUserLoggingIn extends LEvent {
    constructor(username = '', password = '', sender, recipient, event_id = undefined) {
        super(event_id);
        this.serializable_attributes = ['username, password'];
        this.lifecycle_map_event_to_hooks = {
            [LEUserLoggedIn.constructor.name]: 'onsuccess',
            [LEException.constructor.name]: 'onerror',
        };
        this.username = username;
        this.password = password;
        this.construct(sender, recipient);
        this.validate_params();
    }
}
exports.LEUserLoggingIn = LEUserLoggingIn;
LEUserLoggingIn.event = 'user-logging-in';
class LEUserLoggedIn extends LEvent {
    constructor(firstname, surname, cardnumber, password, sender, recipient, event_id = undefined) {
        super(event_id);
        this.serializable_attributes = ['firstname, surname, cardnumber, password'];
        this.lifecycle_map_event_to_hooks = {
            [LEUserLoggedIn.constructor.name]: 'onsuccess',
            [LEException.constructor.name]: 'onerror',
        };
        this.firstname = firstname;
        this.surname = surname;
        this.cardnumber = cardnumber;
        this.password = password;
        this.construct(sender, recipient);
        this.validate_params();
    }
}
exports.LEUserLoggedIn = LEUserLoggedIn;
LEUserLoggedIn.event = 'user-logged-in';
class LEUserLoginAbort extends LEvent {
    constructor(sender, recipient, event_id = undefined) {
        super(event_id);
        this.construct(sender, recipient);
    }
}
exports.LEUserLoginAbort = LEUserLoginAbort;
LEUserLoginAbort.event = 'user-login-abort';
class LEException extends LEvent {
    constructor(e, sender, recipient, event_id = undefined) {
        super(event_id);
        this.serializable_attributes = ['exception'];
        if (e instanceof Error) {
            this.e = e;
            this.exception = e.message + "\n" + e.stack;
        }
        else {
            this.exception = e;
        }
        this.construct(sender, recipient);
        this.validate_params();
    }
}
exports.LEException = LEException;
LEException.event = 'exception';
class LEUserLoginFailed extends LEException {
}
exports.LEUserLoginFailed = LEUserLoginFailed;
LEUserLoginFailed.event = 'user-login-failed';
/**
 * Trigger the server to send mocked RFID tag reads and barcode reads
 */
class LETestMockDevices extends LEvent {
    constructor(event_id = undefined) {
        super(event_id);
        this.default_dispatch = 'server';
        this.serializable_attributes = [];
    }
}
exports.LETestMockDevices = LETestMockDevices;
LETestMockDevices.event = 'test-mock-devices';
