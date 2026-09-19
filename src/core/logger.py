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

    log_file = settings.LOG_DIR / 'waitress_{time:YYYY-MM-DD}.log'

    logger.add(
        log_file,
        format=fmt,
        diagnose=False,
        backtrace=False,
        colorize=False,
        enqueue=True,
        level='INFO',
        encoding='utf-8',
        rotation='00:00',
        retention='14 days',
    )
