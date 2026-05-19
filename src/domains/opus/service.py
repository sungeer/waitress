import time

from src.core import db
from src.core.executor import db_threadpool
from src.domains.opus import repository
from src.utils.concurrency import run_in_threadpool


async def create_conversation(title):
    thread_id = str(int(time.time() * 1000))

    def run_sync():
        with db.begin() as cursor:
            repository.create_conversation(cursor, thread_id, title)

    await run_in_threadpool(db_threadpool, run_sync)
    return thread_id


async def get_conversation(thread_id):
    def run_sync():
        with db.connect() as cursor:
            return repository.get_conversation(cursor, thread_id)

    return await run_in_threadpool(db_threadpool, run_sync)


async def get_messages(conversation_id):
    def run_sync():
        with db.connect() as cursor:
            return repository.get_messages(cursor, conversation_id)

    return await run_in_threadpool(db_threadpool, run_sync)


async def insert_message(conversation_id, user_content, assistant_content):
    def run_sync():
        with db.begin() as cursor:
            repository.insert_message(cursor, conversation_id, 'user', user_content)
            repository.insert_message(cursor, conversation_id, 'assistant', assistant_content)

    await run_in_threadpool(db_threadpool, run_sync)


def sync_insert_message(conversation_id, user_content, assistant_content):
    with db.begin() as cursor:
        repository.insert_message(cursor, conversation_id, 'user', user_content)
        repository.insert_message(cursor, conversation_id, 'assistant', assistant_content)
