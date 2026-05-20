from contextlib import suppress

from loguru import logger
from pymilvus import connections, Collection

from src.core.config import settings


class _MilvusRegistry:

    def __init__(self):
        self._ready = False

    def init(self):
        try:
            connections.connect(
                host=settings.rag_host,
                port=settings.rag_port,
            )
        except (Exception,):
            logger.exception('连接知识库失败')
        else:
            self._ready = True

    def close(self):
        with suppress(Exception):
            connections.disconnect('default')
        self._ready = False

    def collection(self, name):
        if not self._ready:
            raise RuntimeError('milvus registry has not been initialized')
        col = Collection(name)
        col.load()
        return col


milvus_registry = _MilvusRegistry()  # milvus_registry.collection('kb_name') 获取并加载 Milvus 集合
