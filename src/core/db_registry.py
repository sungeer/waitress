from sqlalchemy import create_engine

from src import settings


class _EngineHolder:

    def __init__(self):
        self._engine = None

    def init(self):
        self._engine = create_engine(
            settings.DB_URL,
            echo=False,  # 不打印SQL语句
            pool_size=5,  # 空闲连接 上限（平时保持 5 条）
            max_overflow=15,  # 高峰额外最多再开 15 条（峰值共 20 条）
            pool_timeout=30,  # 取连接等待 30s 失败就报错
            pool_recycle=1800,  # 回收重连
            pool_pre_ping=True,  # 避免拿到失效连接
            connect_args={
                'connect_timeout': 10,  # 连不上 DB 时 10s 快速失败
                'read_timeout': 30,  # 读挂死最多等 30s
                'write_timeout': 30,  # 写挂死最多等 30s
            },
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
