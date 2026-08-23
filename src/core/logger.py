import sys

from loguru import logger

from src import settings


def _formatter(record):
    # 请求内记录（中间件 contextualize 绑定 trace_id）显示 [id]，请求外的直接省略该段
    trace_id = record['extra'].get('trace_id')
    tid = f'[{trace_id}] - ' if trace_id else ''
    return (
        f'{{time:YYYY-MM-DD HH:mm:ss}} - {tid}'
        '{level} - {name}:{function}:{line} - {message}\n{exception}'
    )


def setup_logger():
    logger.remove()

    if settings.ENVIRONMENT == 'development':
        logger.add(
            sys.stdout,
            format=_formatter,
            diagnose=False,
            backtrace=False,
            colorize=False,
            enqueue=True,
            level='INFO',
        )
    else:
        # 非 development（testing / production）→ 日志文件
        logger.add(
            settings.LOG_FILE,
            format=_formatter,
            diagnose=False,
            backtrace=False,
            colorize=False,
            enqueue=True,
            level='INFO',
            encoding='utf-8',
        )
