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
        let i18n_key = 'Exception/'+cast_exception(states['exception'])
        trans_states[i18n_key] = true
      }
      else {
        trans_states['State/'+key] = true
      }
    }
  }
  return trans_states
}

/**
 *
 * @param {exception} exception_object
 * {'exception': {'trace': "(<urllib3.connection.VerifiedHTTPSConnection object at 0xafc683f0>, 'Connection to demo1.intra.koha-helsinki-2.hypernova.fi timed out. (connect timeout=2.5)')",
                  'type': 'ILSConnectionFailure'}}
 */
function cast_exception(exception_object) {
  return exception_object.type
}

//function get_translation_string(exception)