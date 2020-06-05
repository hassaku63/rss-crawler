import logging

LOGGING_FORMAT = '%(asctime)s:%(levelname)s:%(name)s:%(message)s'


def get_logger(name: str) -> logging.Logger:
    log = logging.getLogger(name)
    log.setLevel(logging.INFO)
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter(LOGGING_FORMAT))
    log.addHandler(handler)
    return log