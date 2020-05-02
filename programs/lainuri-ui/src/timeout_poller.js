'use strict';

/**
 * Singleton interval timer which periodically checks should a timeout happen.
 * Timeout is extended py prod:ing the timer
 * Vue.js build pipeline makes sure this file is namespaced
 */

let timeout_poller = 0;
let last_prod = 0;

function start(callback, timeout) {
  last_prod = Date.now();
  timeout_poller = window.setInterval(() => {
    if ((Date.now() - last_prod) > timeout) {
      terminate();
      callback();
    }
  }, 5000);
}

function prod() {
  last_prod = Date.now();
}

function terminate() {
  window.clearInterval(timeout_poller);
}
