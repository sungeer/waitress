from contextlib import asynccontextmanager

from src.core.logger import setup_logger
from src.core import db
from src.core.executor import db_threadpool, bio_threadpool
from src.core.startup_state import startup_state
from src.ai.llm_registry import llm_registry
from src.agents.graph_registry import graph_registry
# from src.ai.milvus_registry import milvus_registry


@asynccontextmanager
async def lifespan(app):
    setup_logger()

    db.init()
    startup_state.db_pool_ready = True

    llm_registry.init()

    # milvus_registry.init()

    graph_registry.init()

    startup_state.app_started = True

    yield

    llm_registry.close()

    # milvus_registry.close()

    db_threadpool.shutdown(wait=True)
    bio_threadpool.shutdown(wait=True)
