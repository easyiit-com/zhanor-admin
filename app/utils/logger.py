import os
import logging
from logging import StreamHandler

class FilepathLogHandler(StreamHandler):
    def format(self, record):
        record.filepath = os.path.abspath(record.pathname)
        message = super().format(record)
        return f"[{record.filepath}] {message}"

def setup_logger(name):
    formatter = logging.Formatter(fmt='%(asctime)s %(levelname)-8s [%(filepath)s:%(lineno)d] %(message)s')

    handler = FilepathLogHandler()
    handler.setFormatter(formatter)

    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    logger.addHandler(handler)

    return logger

# 使用自定义的 Logger
logger = setup_logger(__name__)