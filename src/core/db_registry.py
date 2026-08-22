from sqlalchemy import create_engine

from src import settings


class _EngineHolder:

    def __init__(self):
        self._engine = None

    def init(self):
        self._engine = create_engine(
            settings.DB_URL,
            echo=False,  # 不打印SQL语句
            pool_size=5,  # 空闲连接 上限
            max_overflow=7,  # 高峰额外最多再开 10 条
            pool_timeout=30,  # 取连接等待 30s 失败就报错
            pool_recycle=1800,  # 回收重连
            pool_pre_ping=True,  # 避免拿到失效连接
        )

    def get(self):
        if self._engine is None:
            raise RuntimeError('Engine not initialized')
        return self._engine

    def connect(self):
        return self.get().connect()

    def dispose(self):
        if self._engine is not None:
            self._engine.dispose()


db = _EngineHolder()
