import sys

from loguru import logger

from src import settings


def _inject_request_id(record):
    record['extra'].setdefault('request_id', '-')


def setup_logger():
    logger.remove()

    logger.configure(patcher=_inject_request_id)

    fmt = (
        '{time:YYYY-MM-DD HH:mm:ss.SSS} - [{extra[request_id]}] - {level} - '
        '{name}:{function}:{line} - {message}'
    )

    if settings.ENVIRONMENT == 'development':
        logger.add(
            sys.stdout,
            format=fmt,
            diagnose=False,
            backtrace=False,
            colorize=False,
            enqueue=False,
            level='INFO',
        )

    logger.add(
        settings.LOG_FILE,
        format=fmt,
        diagnose=False,
        backtrace=False,
        colorize=False,
        enqueue=True,
        level='INFO',
        encoding='utf-8',
        rotation='200 MB',
        retention=2,
    )
