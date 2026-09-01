from contextlib import asynccontextmanager

from src.core.logger import setup_logger
from src.core.db_registry import db
from src.core.executor import executor
from src.core.http_client import httpx
from src.core.queue import queue


@asynccontextmanager
async def lifespan(app):
    _ = app

    setup_logger()

    httpx.init()

    db.init()

    queue.init()

    executor.init()

    yield

    await httpx.aclose()

    db.dispose()

    queue.close()

    executor.shutdown()
