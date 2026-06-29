from contextlib import contextmanager, suppress

import pymysql
from pymysql.cursors import DictCursor
from dbutils.pooled_db import PooledDB

from src.config import settings


class _DBPoolHolder:

    def __init__(self):
        self._pool = None

    def init(self):
        """
        启动时只建 2 个，平时池里最多攒 3 个空闲，高峰期不够就涨到 8（maxconnections），低谷时多出来的会自动回收
        """
        self._pool = PooledDB(
            creator=pymysql,
            maxconnections=8,  # 最大连接 含空闲和被借出的
            mincached=2,  # 初始化时预创建的连接数
            maxcached=3,  # 连接归还时，池中最多保留的空闲连接数 必须 >=mincached
            blocking=False,  # 连接用尽时直接抛异常
            ping=1,  # 取连接前 ping
            cursorclass=DictCursor,
            autocommit=False,
            host=settings.db_host,
            port=settings.db_port,
            user=settings.db_user,
            password=settings.db_passwd,
            database=settings.db_name,
            charset='utf8mb4',
            read_timeout=30,  # pymysql
            write_timeout=30,
            connect_timeout=10,
        )

    @contextmanager
    def connect(self):
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
    def begin(self):
        if self._pool is None:
            raise RuntimeError('db pool not initialized')
        conn = self._pool.connection()
        cursor = None
        try:
            conn.begin()
            cursor = conn.cursor()
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
