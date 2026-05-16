import time

from src.core import db


def create_conversation(cursor, thread_id, title):
    now = int(time.time())
    cursor.execute(
        'INSERT INTO conversations (thread_id, title, created_at) VALUES (?, ?, ?)',
        (thread_id, title, now)
    )


def get_conversation(cursor, thread_id):
    cursor.execute('SELECT id FROM conversations WHERE thread_id = ?', (thread_id,))
    row = cursor.fetchone()
    return row['id'] if row else None


def get_messages(cursor, conversation_id):
    cursor.execute(
        'SELECT role, content FROM messages WHERE conversation_id = ? ORDER BY id',
        (conversation_id,)
    )
    return [{'role': r['role'], 'content': r['content']} for r in cursor.fetchall()]


def insert_message(cursor, conversation_id, role, content):
    now = int(time.time())
    cursor.execute(
        'INSERT INTO messages (conversation_id, role, content, created_at) VALUES (?, ?, ?, ?)',
        (conversation_id, role, content, now)
    )
