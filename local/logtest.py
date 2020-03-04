import logging
# create logger
logger_name = "example"
logger = logging.getLogger(logger_name)
logger.setLevel(logging.DEBUG)

# create file handler
log_path = "./loggingDemo-direct.log"
fh = logging.FileHandler(log_path)
fh.setLevel(logging.WARNING)

# create formatter
fmt = '%(asctime)s [%(threadName)s] [%(name)s] [%(levelname)s] %(filename)s[line:%(lineno)d] %(message)s'
datefmt = '%Y-%m-%d %H:%M:%S'
formatter = logging.Formatter(fmt, datefmt)

# add handler and formatter to logger
fh.setFormatter(formatter)
logger.addHandler(fh)

logger.debug('log debug')
logger.info('log info')
logger.warning('log warning')
logger.error('log error')
logger.critical('log critical')
