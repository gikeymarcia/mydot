# https://realpython.com/python-logging/
import logging


# IMPORTANT Only the first .basicConfig() configuration is accepted
# Alternatives logging policies are provided so you can easily change
# the way logs are being used

log_format = "%(asctime)s %(levelname)s [%(funcName)s] %(message)s"
log_level = logging.DEBUG
log_level = logging.INFO
log_filename = "app.log"

# debug log to console
logging.basicConfig(
    level=log_level,
    format=log_format,
)

# debug log to file (overwrite each run)
logging.basicConfig(
    level=log_level,
    filename=log_filename,
    filemode="w",
    format=log_format,
)

# debug log to file (append to log)
logging.basicConfig(
    level=log_level,
    filename=log_filename,
    filemode="a",
    format=log_format,
)
