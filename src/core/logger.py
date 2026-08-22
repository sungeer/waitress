import sys

from loguru import logger

from src.core.context import request_id_var


def setup_logger():
    logger.remove()

    def inject_request_id(record):
        record['extra']['request_id'] = request_id_var.get()

    logger.configure(patcher=inject_request_id)

    fmt = '{time:YYYY-MM-DD HH:mm:ss} - {level} - [{extra[request_id]}] {name}:{function}:{line} - {message}'

    logger.add(
        sink=sys.stdout,
        format=fmt,
        diagnose=False,
        backtrace=False,
        colorize=False,
        enqueue=True,
        level='INFO',
    )
