from contextlib import asynccontextmanager

from src.core.logger import setup_logger
from src.core.db_registry import db
from src.core.executor import executor


@asynccontextmanager
async def lifespan(app):
    _ = app

    setup_logger()

    db.init()

    executor.init()

    yield

    executor.shutdown()

    db.dispose()
