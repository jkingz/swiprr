import logging

from core.settings.base import LOG_FILENAME


class PrintLogFilter(logging.Filter):
    """
    Intercepts logs on when logging so we print it properly
    """

    def filter(self, log):

        message = log.msg

        if isinstance(log.msg, str):
            # Parser/ddf_client was originally made from python 2
            # that's why stirng format here, looks like this.
            # Better to track down, every log string format
            # and change to python 3 if we have the time
            message = log.msg % log.args

        print(f"[Log]: {message}")
        if log.levelno >= logging.ERROR:
            print(f"Log: {log.pathname} in line {log.lineno}")
            print("=========================================")

        return True


log_filehandler = logging.handlers.RotatingFileHandler(
    LOG_FILENAME, "a", 1024 * 1024, 10, None, False
)

logging.basicConfig(
    format="%(asctime)s.%(msecs)03d %(filename)- 15s:%(lineno)-4s %(funcName)-30s %(levelname)-8s %(message)s",
    datefmt="%m-%d %H:%M:%S",
    handlers=[log_filehandler],
)


logging.basicConfig(
    format="%(asctime)s.%(msecs)03d %(filename)- 15s:%(lineno)-4s %(funcName)-30s %(levelname)-8s %(message)s",
    datefmt="%m-%d %H:%M:%S",
)

logger = logging.getLogger(__name__)
# logger.addFilter(PrintLogFilter())
logger.setLevel(logging.DEBUG)
