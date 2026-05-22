from contextlib import contextmanager, suppress

import pymysql
from pymysql.cursors import DictCursor
from dbutils.pooled_db import PooledDB

from src.config import settings


class _DBPoolHolder:

    def __init__(self):
        self._pool = None

    def init(self):
        self._pool = PooledDB(
            creator=pymysql,
            maxconnections=12,
            mincached=5,
            maxcached=5,
            blocking=False,  # 连接用尽时直接抛异常
            ping=1,  # 取连接前 ping
            # cursorclass=DictCursor,
            autocommit=False,
            host=settings.db_host,
            port=settings.db_port,
            user=settings.db_user,
            password=settings.db_passwd,
            database=settings.db_name,
            charset='utf8mb4',
        )

    # LLM 专用
    @contextmanager
    def raw(self):
        if self._pool is None:
            raise RuntimeError('db pool not initialized')
        conn = self._pool.connection()
        cursor = None
        try:
            cursor = conn.cursor()
            yield cursor
        finally:
            if cursor is not None:
                with suppress(Exception):
                    cursor.close()
            with suppress(Exception):
                conn.close()

    @contextmanager
    def connect(self):
        if self._pool is None:
            raise RuntimeError('db pool not initialized')
        conn = self._pool.connection()
        cursor = None
        try:
            cursor = conn.cursor(DictCursor)
            yield cursor
        finally:
            if cursor is not None:
                with suppress(Exception):
                    cursor.close()
            with suppress(Exception):
                conn.close()

    @contextmanager
    def begin(self):
        if self._pool is None:
            raise RuntimeError('db pool not initialized')
        conn = self._pool.connection()
        cursor = None
        try:
            conn.begin()
            cursor = conn.cursor(DictCursor)
            yield cursor
            conn.commit()
        except (Exception,):
            conn.rollback()
            raise
        finally:
            if cursor is not None:
                with suppress(Exception):
                    cursor.close()
            with suppress(Exception):
                conn.close()  # 归还到连接池

    def dispose(self):
        if self._pool is not None:
            self._pool.close()
            self._pool = None


db = _DBPoolHolder()
