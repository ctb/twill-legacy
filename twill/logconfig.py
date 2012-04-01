"""
Module for configuring logging.
"""
import sys
import logging

loglevels = {
    "CRITICAL" : logging.CRITICAL,
    "ERROR" : logging.ERROR,
    "WARNING" : logging.WARNING,
    "INFO" : logging.INFO,
    "DEBUG" : logging.DEBUG,
    "NOTSET" : logging.NOTSET,
}

logger = logging.getLogger()
handler = logging.StreamHandler(sys.stdout)
logger.addHandler(handler)

logger.setLevel(logging.INFO)

def set_handler_for_stream(stream):
    global handler
    logger.removeHandler(handler)
    handler = logging.StreamHandler(stream)
    logger.addHandler(handler)

