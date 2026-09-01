# RQ 任务队列

RQ 用于把耗时任务从 web 进程剥离到独立 worker 进程执行，请求丢任务进队列后直接返回。

- `src/core/queue.py` — 队列管理（web 进程 enqueue 用），在 `lifespan` 里 init/close
- `worker.py` — worker 进程入口（独立进程，消费任务用）
- `docs/devops/rq_start.sh` / `rq_stop.sh` — 生产环境启停 worker

## 1. 定义任务

在对应领域的 `tasks.py` 定义任务函数。RQ 要求 job 函数**必须是模块顶层可导入、可 pickle 的普通函数**，不能是闭包或 lambda。

```python
# src/domains/users/tasks.py
from loguru import logger


def send_welcome_email(user_id: int, email: str):
    # 这里是真正耗时的工作，例如调用邮件服务、生成报表等
    logger.info('send welcome email user_id={} email={}', user_id, email)
```

## 2. 投递任务

在 service 层调用 `queue.get().enqueue(...)`。enqueue 是一次 Redis 写（毫秒级），按项目「阻塞 IO 走线程池」的惯例包进 `run_in_threadpool`。

```python
# src/domains/users/service.py
from src.core.executor import executor
from src.core.queue import queue
from src.utils.concurrency import run_in_threadpool


async def create_user(username, display_name, email):
    # ... 原有建号逻辑
    user_id = ...

    # 异步投递欢迎邮件任务，这里只入队，不等待任务执行完
    await run_in_threadpool(
        executor.bio,
        queue.get().enqueue,
        'src.domains.users.tasks.send_welcome_email',  # 用字符串路径，worker 按此导入
        user_id,
        email,
    )
    return user_id
```

可选参数（RQ 选项，会从函数参数中分离、不会传给任务函数）：

```python
from rq import Retry

queue.get().enqueue(
    'src.domains.users.tasks.send_welcome_email',
    user_id,
    email,
    job_timeout=60,          # 任务最长执行时间（秒），默认 180
    retry=Retry(max=3, interval=[10, 60, 300]),  # 失败重试
    description='send welcome email',            # 便于在后台查看
)
```

## 3. 启动 worker

```bash
# 生产（Linux），由 docs/devops/rq_start.sh 拉起
/srv/venvs/waitress/bin/python worker.py

# 本地开发（Windows）：worker.py 已自动改用 SimpleWorker
.venv\Scripts\python.exe worker.py
```

## 4. 日志

worker 进程的日志分两个文件，互不混入：

| 文件 | 内容 | 机制 |
|---|---|---|
| `RQ_LIFECYCLE_LOG`（生产默认 `/srv/logs/rq_lifecycle.log`） | worker 生命周期：启动/停止、dequeue、job 完成/失败 | RQ 标准 logging，`worker.py` 里提前给 `rq` logger 挂 FileHandler，RQ 检测到已有 handler 后不再输出到 stdout |
| `LOG_FILE`（生产由 `rq_start.sh` 覆盖为 `/srv/logs/rq.log`） | 任务函数里的业务日志 | loguru，带 `{time} - [{trace_id}] - {level}` 格式 |

两个路径分别由环境变量 `RQ_LIFECYCLE_LOG`、`LOG_FILE` 控制（见 `rq_start.sh`）。

## 注意事项

- `queue.get()` 未初始化时抛 `RuntimeError`，与 `db.get()` 行为一致；web 进程里由 `lifespan` 保证已 init。
- **trace_id 不跨进程**：enqueue 时不带请求上下文，任务函数里的 `logger` 日志 `trace_id` 为 `-`。若需要任务日志关联到原始请求，把 `trace_id` 作为参数显式传进任务函数。
- 任务函数抛异常会进入 RQ 的 FailedJobRegistry，可配置 `retry` 自动重试。
- 生产 worker 用默认 `Worker`（fork 子进程执行，job 崩溃不影响 worker）；Windows 不支持 `os.fork`，`worker.py` 自动切 `SimpleWorker`（同进程执行）。
