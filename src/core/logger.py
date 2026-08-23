import logging

import structlog
from structlog.processors import CallsiteParameter, CallsiteParameterAdder


def setup_logger():
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
        logger_factory=structlog.PrintLoggerFactory(),  # 输出到 stdout
        cache_logger_on_first_use=False,  # 配合 merge_contextvars 不缓存绑定
    )
