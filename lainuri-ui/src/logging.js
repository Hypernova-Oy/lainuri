const winston = require('winston');

const root_logger = winston.createLogger({
  level: 'debug',
  format: winston.format.json(),
  defaultMeta: { service: 'root' },
  transports: [
    new winston.transports.Console(),
    //new winston.transports.File({ filename: 'error.log', level: 'error' }),
    //new winston.transports.File({ filename: 'combined.log' })
  ]
});
module.exports = root_logger;

//const logger = root_logger.child({service: 'main'});
//exports.logger = logger;
