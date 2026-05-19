import sqlite3
from contextlib import contextmanager, suppress

from src.core.config import settings


def init():
    conn = sqlite3.connect(f'{settings.db_path}')
    try:
        conn.execute('PRAGMA journal_mode=WAL')
        conn.execute('PRAGMA synchronous=NORMAL')
        conn.execute('PRAGMA journal_size_limit=67108864')

        # 会话表
        conn.execute('''
            CREATE TABLE IF NOT EXISTS conversations (
                id         INTEGER PRIMARY KEY,
                thread_id  TEXT    NOT NULL UNIQUE,
                title      TEXT    NOT NULL,
                created_at INTEGER NOT NULL
            )
        ''')

        # 消息表
        conn.execute('''
            CREATE TABLE IF NOT EXISTS messages (
                id              INTEGER PRIMARY KEY,
                conversation_id INTEGER NOT NULL,
                role            TEXT    NOT NULL,
                content         TEXT    NOT NULL,
                created_at      INTEGER NOT NULL
            )
        ''')
        conn.execute(
            'CREATE INDEX IF NOT EXISTS idx_conversation_id '
            'ON messages(conversation_id)'
        )

        # 审批任务表
        conn.execute('''
            CREATE TABLE IF NOT EXISTS approval_tasks (
                id            INTEGER PRIMARY KEY,
                thread_id     TEXT    NOT NULL UNIQUE,
                order_id      TEXT    NOT NULL DEFAULT '',
                status        INTEGER NOT NULL DEFAULT 0,
                created_at    INTEGER NOT NULL,
                updated_at    INTEGER NOT NULL
            )
        ''')
        conn.execute(
            'CREATE INDEX IF NOT EXISTS idx_status '
            'ON approval_tasks(status)'
        )
    finally:
        conn.close()


# LLM 专用
@contextmanager
def raw():
    conn = sqlite3.connect(f'{settings.db_path}')
    conn.execute('PRAGMA busy_timeout=5000')
    conn.execute('PRAGMA cache_size=-20000')
    conn.execute('PRAGMA temp_store=MEMORY')
    conn.execute('PRAGMA mmap_size=268435456')
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
def connect():
    conn = sqlite3.connect(f'{settings.db_path}')
    conn.execute('PRAGMA busy_timeout=5000')
    conn.execute('PRAGMA cache_size=-20000')
    conn.execute('PRAGMA temp_store=MEMORY')
    conn.execute('PRAGMA mmap_size=268435456')
    conn.row_factory = sqlite3.Row  # 既能用下标，又能用键名
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
def begin():
    conn = sqlite3.connect(f'{settings.db_path}')
    conn.execute('PRAGMA busy_timeout=5000')
    conn.execute('PRAGMA cache_size=-20000')
    conn.execute('PRAGMA temp_store=MEMORY')
    conn.execute('PRAGMA mmap_size=268435456')
    conn.row_factory = sqlite3.Row  # 既能用下标，又能用键名
    cursor = None
    try:
        cursor = conn.cursor()
        cursor.execute('BEGIN IMMEDIATE')
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
            conn.close()
