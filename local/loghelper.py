import logging
from functools import partial


# create formatter
fmt = '%(asctime)s [%(threadName)s] [%(name)s] [%(levelname)s] %(filename)s[line:%(lineno)d] %(message)s'
datefmt = '%Y-%m-%d %H:%M:%S'
formatter = logging.Formatter(fmt, datefmt)


# partial basicConfig
basicConfig = partial(logging.basicConfig, format=fmt, datefmt=datefmt, level=logging.INFO)


# create file handler
def get_fh(filename, **kwargs):
    fh = logging.FileHandler(filename)
    fh.setLevel(kwargs.get("level") or logging.INFO)
    fh.setFormatter(kwargs.get("formatter") or formatter)
    return fh


if __name__ == '__main__':
    logger_name = "example"
    logger = logging.getLogger(logger_name)
    logger.addHandler(get_fh(logger_name))
    logger.setLevel(logging.DEBUG)
    logger.debug('log debug')
    logger.info('log info')
    logger.warning('log warning')
    logger.error('log error')
    logger.critical('log critical')
