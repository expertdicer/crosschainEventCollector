import logging


def logging_basic_config(filename=None):
    format = '%(asctime)s - %(name)s [%(levelname)s] - %(message)s'
    if filename is not None:
        logging.basicConfig(level=logging.INFO, format=format, filename=filename)
    else:
        logging.basicConfig(level=logging.INFO, format=format)


def logging_debug_config(filename=None):
    format = '%(asctime)s - %(name)s [%(levelname)s] - %(message)s'
    if filename is not None:
        logging.basicConfig(level=logging.DEBUG, format=format, filename=filename)
    else:
        logging.basicConfig(level=logging.DEBUG, format=format)


def config_log(level=logging.INFO):
    format = '%(asctime)s - %(name)s [%(levelname)s] - %(message)s'
    logging.basicConfig(
        format=format,
        level=level,
        datefmt='%Y-%m-%d %H:%M:%S')