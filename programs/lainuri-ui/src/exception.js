// rfid.py
class RFIDException extends Error {
}

class RFIDCommand extends RFIDException {
}

class TagNotDetected extends RFIDException {
}

class GateSecurityStatusVerification extends RFIDException {
}

// ils.py
class ILSException extends Error {
}

class InvalidUser extends ILSException {
}

class NoUser extends ILSException {
}

class NoItem extends ILSException {
}

const classes = {
  RFIDException,
  RFIDCommand,
  TagNotDetected,
  GateSecurityStatusVerification,
  ILSException,
  InvalidUser,
  NoUser,
  NoItem,
}


export function translate_exception(e) {
  if (!e.exception) return '';
  let exception = cast_exception(e.exception);
  return exception+""; // TODO: Here we would use a translation key to fetch the proper translation from globalize
}

function cast_exception(e_str) {
  let e_class = classes[e_str]
  if (!e_class) {
    console.error(`cast_exception():> Unknown exception class for exception string '${e_str}'`);
    return e_str;
  }
  return e_class(e_str);
}
