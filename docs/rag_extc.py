import time
from typing import List

from openai import OpenAI
from loguru import logger
from pymilvus import connections, Collection

from src.core.config import settings
from src.ai.rag_registry import rag_registry


# 向量化 用户的提问
def to_embedding(text: str) -> List[float]:
    client: OpenAI = rag_registry()

    texts = [text]

    embeddings = None

    max_retries = 3
    for attempt in range(1, max_retries + 1):
        try:
            embeddings = client.embeddings.create(
                model=settings.rag_model,
                input=texts,
            )
            break
        except (Exception,):
            logger.exception(f'向量化失败第[{attempt}]次')
            if attempt < max_retries:
                time.sleep(3)

    if embeddings is None:
        raise RuntimeError('向量化失败')

    logger.info(f'embedding维度为：{len(embeddings.data)}')

    response = [data.embedding for data in embeddings.data]
    embedding = response[0]
    return embedding


# 获取向量集合
def get_kb_collection(collection_name: str):
    collection = Collection(collection_name)

    logger.info('collection load ...')

    collection.load()

    logger.info('collection load ok')
    return collection
