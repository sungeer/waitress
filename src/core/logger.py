import sys

from loguru import logger

from src import settings

_LEVEL_ABBR = {
    'TRACE': 'TRC',
    'DEBUG': 'DBG',
    'INFO': 'INF',
    'SUCCESS': 'SUC',
    'WARNING': 'WRN',
    'ERROR': 'ERR',
    'CRITICAL': 'CRT'
}


def _patch_record(record):
    record['extra'].setdefault('request_id', '-')
    record['level'].name = _LEVEL_ABBR.get(record['level'].name, record['level'].name)


def setup_logger():
    logger.remove()

    logger.configure(patcher=_patch_record)

    fmt = (
        '{time:HH:mm:ss.SSS} | {extra[request_id]} | {level} | '
        '{message} ({name}:{line})'
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
