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




class ExceptionCastingException extends ILSException {
}

const classes = {
  ExceptionCastingException,
  RFIDCommand,
  TagNotDetected,
  GateSecurityStatusVerification,
  InvalidUser,
  NoUser,
  NoItem,

  not_checked_out: 'not_checked_out',
  return_to_another_branch: 'return_to_another_branch',
  needs_confirmation: 'needs_confirmation',
}

/**
 *
 * @param  {...any} args
 * @returns {Map of i18n_keys}
 */
export function translate_exception(...args) {
  let trans_states = {}
  for (let arg_i in args) {
    let states = args[arg_i]
    for (let key in states) {
      if (key === 'exception') {
        let i18n_key = cast_exception(states[key])
        trans_states[i18n_key] = true
      }
      else {
        trans_states[key] = true
      }
    }
  }
  return trans_states
}

function cast_exception(exception_object) {
  let e_class = classes[exception_object.type]
  if (!e_class) {
    return `ExceptionCastingException("Unknown exception class for exception string '${exception_object.type}' '${exception_object.trace}'")`;
  }
  return exception_object.type
}

//function get_translation_string(exception)