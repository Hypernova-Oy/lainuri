'use strict';

/**
 * Singleton interval timer which periodically checks should a timeout happen.
 * Timeout is extended py prod:ing the timer
 * Vue.js build pipeline makes sure this file is namespaced
 */

import {get_logger} from './logger'
let log = get_logger('timeout_poller.js');

let timeout_pollers = {};
let interval_pollers = {};
let last_prods = {};

function start(timer_name, timer_callback, timer_timeout, interval_callback, interval_timeout) {
  log.info(`New timeout '${timer_name}' starting with timer_timeout '${timer_timeout}s', interval_timeout '${interval_timeout}'`);

  if (timer_name === "*") throw new TypeError("The name of the timer cannot be '*', as this targets all timers")

  last_prods[timer_name] = Date.now()/1000;
  if (timer_callback) {
    timeout_pollers[timer_name] = window.setInterval(() => {
      if ((Date.now()/1000 - last_prods[timer_name]) > timer_timeout) {
        terminate(timer_name);
        timer_callback(timer_name);
      }
    }, 4000);
  }
  if (interval_callback) {
    interval_pollers[timer_name] = window.setInterval(() => {
      interval_callback(timer_name);
    }, interval_timeout);
  }
}

function prod(timer_name) {
  if (timer_name === "*") {
    log.info(`Timeout '${timer_name}' prod()`);
    Object.keys(timeout_pollers).forEach(timer_name => prod(timer_name))
  }
  else {
    log.debug(`Timeout '${timer_name}' prod()`)
    does_timer_exists(timer_name)
    last_prods[timer_name] = Date.now()/1000;
  }
}

function terminate(timer_name) {
  if (timer_name === "*") {
    log.info(`Timeout '${timer_name}' terminating`);
    Object.keys(timeout_pollers).forEach(timer_name => terminate(timer_name))
    Object.keys(interval_pollers).forEach(timer_name => terminate(timer_name))
  }
  else {
    if (timeout_pollers[timer_name]) {
      window.clearInterval(timeout_pollers[timer_name]);
      delete timeout_pollers[timer_name];
      delete last_prods[timer_name];
      log.info(`Timeout '${timer_name}' terminating`);
    }
    if (interval_pollers[timer_name]) {
      window.clearInterval(interval_pollers[timer_name]);
      delete interval_pollers[timer_name];
      log.info(`Interval '${timer_name}' terminating`);
    }
  }
}

function does_timer_exists(timer_name) {
  if (! timeout_pollers[timer_name]){
    throw new ReferenceError(`Unknown timer '${timer_name}'`)
  }
}

export {start, prod, terminate};
