import logging
from pathlib import Path

import structlog
from structlog.processors import CallsiteParameter, CallsiteParameterAdder

from src import settings


def setup_logger():
    if settings.ENVIRONMENT == 'development':
        # 开发环境：保持输出到 stdout
        logger_factory = structlog.PrintLoggerFactory()
    else:
        # 非 development（testing / production）：写入日志文件
        log_path = Path(settings.LOG_FILE)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        logger_factory = structlog.WriteLoggerFactory(
            open(log_path, 'a', encoding='utf-8')
        )

    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,  # 合并 contextvars 里的 trace_id
            structlog.processors.add_log_level,  # level 字段
            structlog.processors.TimeStamper(fmt='%Y-%m-%d %H:%M:%S', utc=False),  # 本地时间
            structlog.processors.format_exc_info,  # logger.exception 输出堆栈
            CallsiteParameterAdder(
                [CallsiteParameter.QUAL_MODULE, CallsiteParameter.LINENO]
            ),  # 模块名 + 行号
            structlog.processors.JSONRenderer(ensure_ascii=False),  # JSON Lines，中文不转义
        ],
        wrapper_class=structlog.make_filtering_bound_logger(logging.INFO),
        logger_factory=logger_factory,  # development 输出 stdout，其余写日志文件
        cache_logger_on_first_use=False,  # 配合 merge_contextvars 不缓存绑定
    )
