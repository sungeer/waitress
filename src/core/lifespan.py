from contextlib import asynccontextmanager

from src.core.logger import setup_logger
from src.core.db_registry import db
from src.core.executor import executor
from src.ai.llm_registry import llm_registry
from src.agents.graph_registry import graph_registry


@asynccontextmanager
async def lifespan(app):
    setup_logger()

    db.init()

    llm_registry.init()

    graph_registry.init()

    executor.init()

    yield

    llm_registry.close()

    executor.shutdown()

    db.dispose()
