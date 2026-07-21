import uuid
from contextvars import ContextVar

run_id_var = ContextVar('run_id', default='-')


def new_run_id() -> str:
    run_id = uuid.uuid4().hex[:16]  # 'd8961c3c4f884505'
    return run_id
