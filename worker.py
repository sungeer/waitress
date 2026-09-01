import logging
import os

from redis import Redis
from rq import SimpleWorker, Worker

from src import settings
from src.core.logger import setup_logger


def _setup_lifecycle_logging():
    # RQ 生命周期日志（rq.worker / rq.job 等）走标准 logging。
    # 必须先挂 handler 再 work()：bootstrap 检测到 rq logger 已有 handler 会跳过 stdout，
    # 生命周期日志全部落进 RQ_LIFECYCLE_LOG 文件，与业务日志(loguru 写 LOG_FILE)分开
    handler = logging.FileHandler(settings.RQ_LIFECYCLE_LOG, encoding='utf-8')
    handler.setFormatter(logging.Formatter('%(asctime)s %(message)s', datefmt='%H:%M:%S'))
    rq_logger = logging.getLogger('rq')
    rq_logger.addHandler(handler)
    rq_logger.setLevel(logging.INFO)


def main():
    setup_logger()

    _setup_lifecycle_logging()

    redis = Redis.from_url(settings.REDIS_URL)

    # 生产环境(Linux)用默认 Worker(fork 子进程跑任务);
    # Windows 不支持 os.fork, 本地联调改用 SimpleWorker(同进程执行)
    worker_class = SimpleWorker if os.name == 'nt' else Worker

    worker = worker_class(settings.RQ_QUEUE_NAME, connection=redis)
    worker.work()


if __name__ == '__main__':
    main()
