"""Stores global settings."""
import logging
DEBUG = False

def init_logger(name):
    """Initializes the logger."""
    logging.basicConfig()
    logger = logging.getLogger(name)
    if DEBUG:
        logger.setLevel(logging.DEBUG)
    else:
        logger.setLevel(logging.INFO)
    return logger
