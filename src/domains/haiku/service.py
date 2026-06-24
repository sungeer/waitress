from loguru import logger

from src.core.db_registry import db
from src.core.executor import executor
from src.agents.graph_registry import graph_registry
from src.domains.haiku import repository
from src.utils import rand
from src.utils.concurrency import run_in_threadpool

# 任务状态常量
STATUS_PENDING = 0
STATUS_RUNNING = 1
STATUS_COMPLETED = 2
STATUS_FAILED = 3

STATUS_MAP = {
    STATUS_PENDING: 'pending',
    STATUS_RUNNING: 'running',
    STATUS_COMPLETED: 'completed',
    STATUS_FAILED: 'failed',
}


async def create_conversation(title):
    thread_id = rand.gen_token()

    def run_sync():
        with db.begin() as cursor:
            repository.create_conversation(cursor, thread_id, title)

    await run_in_threadpool(executor.db, run_sync)
    return thread_id


async def get_conversation(thread_id):
    def run_sync():
        with db.connect() as cursor:
            return repository.get_conversation(cursor, thread_id)

    return await run_in_threadpool(executor.db, run_sync)


async def get_messages(conversation_id):
    def run_sync():
        with db.connect() as cursor:
            return repository.get_messages(cursor, conversation_id)

    return await run_in_threadpool(executor.db, run_sync)


async def create_task(thread_id):
    """创建异步任务，返回 task_id"""
    task_id = rand.gen_token()

    def run_sync():
        with db.begin() as cursor:
            repository.create_task(cursor, task_id, thread_id)

    await run_in_threadpool(executor.db, run_sync)
    logger.info(f'任务已创建: task_id={task_id}, thread_id={thread_id}')
    return task_id


def run_graph_task(task_id, thread_id, conversation_id, questions, input_dict, config):
    """后台任务：执行 graph，写结果，更新状态"""
    try:
        _set_status(task_id, STATUS_RUNNING)

        response = graph_registry['haiku'].invoke(input_dict, config)
        msg = response['messages'][-1]
        content = ''.join(msg.content)

        _save_completed(task_id, conversation_id, questions, content)

        logger.info(f'graph task finished: task_id={task_id}')
    except Exception as e:
        logger.exception(f'graph task failed: task_id={task_id}')
        _set_failed(task_id, str(e))


async def get_task_status(task_id):
    """查询任务状态，completed 时带结果内容"""
    def run_sync():
        with db.connect() as cursor:
            task = repository.get_task(cursor, task_id)
            if task is None:
                return None
            result = None
            if task['status'] == STATUS_COMPLETED:
                row = repository.get_result(cursor, task_id)
                if row:
                    result = {'content': row['content']}
            elif task['status'] == STATUS_FAILED:
                result = {'error': task['error_message']}
            return {
                'task_id': task['task_id'],
                'status': STATUS_MAP[task['status']],
                'data': result,
            }

    return await run_in_threadpool(executor.db, run_sync)


def _set_status(task_id, status):
    with db.begin() as cursor:
        repository.update_task_status(cursor, task_id, status)


def _set_failed(task_id, error_message):
    with db.begin() as cursor:
        repository.set_task_failed(cursor, task_id, error_message)


def _save_completed(task_id, conversation_id, questions, content):
    with db.begin() as cursor:
        repository.insert_result(cursor, task_id, content)
        repository.insert_message(cursor, conversation_id, 'user', questions)
        repository.insert_message(cursor, conversation_id, 'assistant', content)
        repository.update_task_status(cursor, task_id, STATUS_COMPLETED)
