from contextlib import asynccontextmanager

from src.core.background import background
from src.core.logger import setup_logger
from src.core.db_registry import db
from src.core.executor import executor
from src.core.llm_registry import llm_registry
from src.agents.graph_registry import graph_registry


@asynccontextmanager
async def lifespan(app):
    setup_logger()

    db.init()

    llm_registry.init()

    graph_registry.init()

    executor.init()

    yield

    # 先取消在途后台任务，再关闭它们依赖的资源
    await background.shutdown()

    llm_registry.close()

    executor.shutdown()

    db.dispose()
