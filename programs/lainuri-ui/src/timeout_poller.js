'use strict';

/**
 * Singleton interval timer which periodically checks should a timeout happen.
 * Timeout is extended py prod:ing the timer
 * Vue.js build pipeline makes sure this file is namespaced
 */

import {get_logger} from './logger'
let log = get_logger('timeout_poller.js');

let timeout_poller = 0;
let last_prod = 0;

function start(callback, timeout) {
  log.info(`New timeout starting '${timeout}s'`);
  last_prod = Date.now()/1000;
  timeout_poller = window.setInterval(() => {
    if ((Date.now()/1000 - last_prod) > timeout) {
      terminate();
      callback();
    }
  }, 5000);
}

function prod() {
  log.debug("Timeout prod()")
  last_prod = Date.now()/1000;
}

function terminate() {
  log.info('Timeout terminating');
  window.clearInterval(timeout_poller);
}

export {start, prod, terminate};
