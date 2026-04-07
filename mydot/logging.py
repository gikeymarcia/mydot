# https://realpython.com/python-logging/
import logging

log_format = "%(asctime)s %(levelname)s [%(funcName)s] %(message)s"
log_level = logging.INFO

logging.basicConfig(
    level=log_level,
    format=log_format,
)
