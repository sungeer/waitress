import sys

from loguru import logger

from src.config import settings
from src.core.context import run_id_var


def setup_logger():
    logger.remove()

    def inject_run_id(record):
        record['extra']['run_id'] = run_id_var.get('-')

    logger.configure(patcher=inject_run_id)

    logger.add(
        settings.log_path,
        rotation='100 MB',
        retention=5,  # 保留最近 5 个轮转文件
        format='{time:YYYY-MM-DD HH:mm:ss} - {level} - [{extra[run_id]}] {name}:{function}:{line} - {message}',
        encoding='utf-8',
        enqueue=True,
        diagnose=False,
        backtrace=False,
        colorize=False,
        level='INFO',
        filter=lambda record: 'task' not in record['extra'],
    )

    logger.add(
        settings.error_log_path,
        rotation='50 MB',
        retention=2,
        format='{time:YYYY-MM-DD HH:mm:ss} - {level} - [{extra[run_id]}] {name}:{function}:{line} - {message}',
        encoding='utf-8',
        enqueue=True,
        diagnose=False,
        backtrace=False,
        colorize=False,
        level='ERROR',
    )

    if settings.environment == 'development':
        logger.add(
            sink=sys.stdout,  # 标准输出流
            format='{time:YYYY-MM-DD HH:mm:ss} - {level} - [{extra[run_id]}] {name}:{function}:{line} - {message}',
            level='INFO',
            diagnose=False,  # 关闭变量值
            backtrace=False,  # 关闭完整堆栈跟踪
            colorize=False,
            enqueue=True,  # 启用异步日志处理
        )
