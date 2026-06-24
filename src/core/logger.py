import sys

from loguru import logger

from src.core.context import run_id_var


def setup_logger():
    logger.remove()

    def inject_run_id(record):
        record['extra']['run_id'] = run_id_var.get()

    logger.configure(patcher=inject_run_id)

    fmt = '{time:YYYY-MM-DD HH:mm:ss} - {level} - [{extra[run_id]}] {name}:{function}:{line} - {message}'

    logger.add(
        sink=sys.stdout,
        format=fmt,
        diagnose=False,
        backtrace=False,
        colorize=False,
        enqueue=True,
        level='INFO',
    )
