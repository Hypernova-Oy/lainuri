"use strict";

import * as log4javascript from "log4javascript";

/**
 * Inject WebsocketAppender to log4javascript
 */
let WebsocketAppender = function (send_message_callback) {
  var initialized = false;
  this.send_message_callback;
  this.send_queue = [];
  this.send_message_callback = send_message_callback;
  this.layout = new log4javascript.PatternLayout("%m{1}");

  this.send_interval_milliseconds = 5000
  this.send_interval = window.setInterval(
    () => this.sendMessageQueue(),
    this.send_interval_milliseconds
  )

  this.toString = function() { return "WebsocketAppender"; }

  this.send_message_response_handler = function(loggingEventResponse) {
    console.log(loggingEventResponse);
  };

  this.setLayout = function(layoutParam) {
    this.layout = layoutParam;
    return this;
  };

  this.append = function(loggingEvent) {
    if (!initialized) {
      this.init();
    }
    this.send_queue.push(loggingEvent);
  };

  this.init = function() {
    initialized = true;
    // Add unload event to send outstanding messages
    var oldBeforeUnload = window.onbeforeunload;
    window.onbeforeunload = function() {
      if (oldBeforeUnload) {
        oldBeforeUnload();
      }
      window.clearInterval(this.send_interval)
      this.sendMessageQueue()
    };
  }

  this.sendMessageQueue = function () {
    if (! this.send_message_callback) return;
    if (this.send_messages_lock) return;
    this.send_messages_lock = true;
    try {
      if (this.send_queue.length > 0 &&
          this.sendMessageChunk(this._buildMessagesChunk())) {
        this.send_queue = [];
      }
    }
    catch (e){
      console.error(e)
    }
    finally {
      this.send_messages_lock = false;
    }
  }

  this._buildMessagesChunk = function () {
    let chunk = [];
    this.send_queue.forEach((loggingEvent) => {
      chunk.push(this._create_log_record_for_transport(loggingEvent));
    });
    return chunk;
  }

  this._create_log_record_for_transport = function (loggingEvent) {
    return {
      level: loggingEvent.level.name,
      logger_name: loggingEvent.logger.name,
      milliseconds: loggingEvent.timeStampInMilliseconds,
      log_entry: this.layout.formatWithException(loggingEvent),
    };
  }

  this.sendMessageChunk = function (chunk) {
    if (this.send_message_callback) return this.send_message_callback(chunk);
  }

  this.setCallbacks = function(send_message_callback) {
    this.send_message_callback = send_message_callback;
  }
};
WebsocketAppender.prototype = new log4javascript.Appender();


class LoggerManager {
  constructor() {
    this.initRootLogger();
    this.initedLoggers = {};
    this.config = {};
  }

  setWebsocketHandlers(send_message_callback) {
    this.websocketAppenderInstance.setCallbacks(send_message_callback);
  }

  /**
   * @param loggerName The name of the logger to get and configure. If nothing is given, returns the root logger.
   * @returns {log4javascript.Logger}
   */
  getLogger(loggerName) {
    let logger;
    if (!loggerName) {
      logger = log4javascript.getRootLogger();
    } else {
      logger = log4javascript.getLogger(loggerName);
    }

    // If logger is named and we haven't initiated that logger yet, proceed to configure it
    if (loggerName && ! this.initedLoggers[loggerName]) {
      this.configureLogger(logger)
    }

    return logger;
  }

  configureLogger(logger) {
    let logger_config = this.config[logger.name]
    if (logger_config) {
      if (logger_config.level) logger.setLevel(logger_config.level)
    }
    // Having a configuration for a named logger is not mandatory. Then it simply inherits configuration from ancestors.

    this.initedLoggers[logger.name] = logger;
  }

  /**
   * Loads configuration from the given log4j configuration text/string or a JSON-object
   *
   * @param configJson, eg. {
   *                           "app.package1.package2": {"level": "FATAL"},
   *                           "app.package1.package3": {"level": "TRACE"},
   *                        }
   */
  loadConfigurations(configJsonOrTxt) {
    let config;
    if (typeof configJsonOrTxt === "string") {
      config = JSON.parse(configJsonOrTxt);
    }
    Object.keys(config).forEach((loggerName) => {
      if (! loggerName.match(/\w+(?:\.\w+)*/)) throw Error(`LoggerManager.loadConfigurations:> Given loggerName '${loggerName}' is invalid!`);

      // Turn level to log4javascript.Level instances
      let level = config[loggerName].level && config[loggerName].level.toUpperCase();
      if (level) {
        for (let l4j_level of Object.keys(log4javascript.Level)) {
          if (l4j_level === level) {
            config[loggerName].level = log4javascript.Level[l4j_level]
            break;
          }
        }
      }
    });
    this.config = config;

    for (let logger of this.initedLoggers) {
      this.configureLogger(logger)
    }
  }

  /**
   * Initializes the root logger, so other instantiated loggers can inherit it's configuration
   */
  initRootLogger() {
    const log = this.getLogger();

    this.websocketAppenderInstance = new WebsocketAppender();
    const appender = new log4javascript.BrowserConsoleAppender();
    // Change the desired configuration options
    appender.setThreshold(log4javascript.Level.ALL);
    this.websocketAppenderInstance.setThreshold(log4javascript.Level.ALL);

    // Define the log layout
    appender.setLayout(new log4javascript.PatternLayout("%d{HH:mm:ss}[%-5p]%c: %m{1}"));

    // Add the appender to the logger
    log.addAppender(appender);
    log.addAppender(this.websocketAppenderInstance);
  }
}


let logger_manager = new LoggerManager();

function get_logger(logger_name) {
  return logger_manager.getLogger(logger_name)
}

// Export the version of log4javascript used by this module. If you import log4javascript from the module using this logger,
// it can import a different version of log4javascript. This is because npm tracks module dependencies by the external module, not by the whole app.
export {get_logger, log4javascript, logger_manager};
