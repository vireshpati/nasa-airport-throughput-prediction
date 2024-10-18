import logging
import sys
from ..utils.config import config

def get_logger(name):
    """
    Configures and returns a logger.

    Parameters:
        name (str): Name of the logger.

    Returns:
        logging.Logger: Configured logger.
    """
    logger = logging.getLogger(name)
    if not logger.handlers:
        logger.setLevel(config.LOG_LEVEL)
        handler = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter(config.LOG_FORMAT)
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    return logger