from redis import Redis
from rq import Queue

from src import settings


class _QueueHolder:

    def __init__(self):
        self._redis = None
        self._queue = None

    def init(self):
        self._redis = Redis.from_url(settings.REDIS_URL)
        self._queue = Queue(settings.RQ_QUEUE_NAME, connection=self._redis)

    def get(self):
        if self._queue is None:
            raise RuntimeError('Queue not initialized')
        return self._queue

    def close(self):
        if self._redis is not None:
            self._redis.close()
        self._redis = None
        self._queue = None


queue = _QueueHolder()
