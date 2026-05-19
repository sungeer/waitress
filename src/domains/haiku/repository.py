import time


def create_conversation(cursor, thread_id, title):
    sql_str = '''
        INSERT INTO conversations (thread_id, title, created_at)
        VALUES (?, ?, ?)
    '''
    now = int(time.time())
    cursor.execute(sql_str, (thread_id, title, now))


def get_conversation(cursor, thread_id):
    sql_str = '''
        SELECT
            id
        FROM
            conversations
        WHERE
            thread_id = ?
    '''
    cursor.execute(sql_str, (thread_id,))
    row = cursor.fetchone()
    return row['id'] if row else None


def get_messages(cursor, conversation_id):
    sql_str = '''
        SELECT
            role, content
        FROM
            messages
        WHERE
            conversation_id = ?
        ORDER BY id
    '''
    cursor.execute(sql_str, (conversation_id,))
    return [{'role': r['role'], 'content': r['content']} for r in cursor.fetchall()]


def insert_message(cursor, conversation_id, role, content):
    sql_str = '''
        INSERT INTO messages (conversation_id, role, content, created_at)
        VALUES (?, ?, ?, ?)
    '''
    now = int(time.time())
    cursor.execute(sql_str, (conversation_id, role, content, now))


def get_pending(cursor, thread_id):
    sql_str = '''
        SELECT
            thread_id, order_id, amount, risk_level,
            content, approver_id
        FROM
            approval_tasks
        WHERE
            thread_id = ?
            AND status = 0
    '''
    cursor.execute(sql_str, (thread_id,))
    return cursor.fetchone()


def approve(cursor, thread_id, operator):
    sql_str = '''
        UPDATE
            approval_tasks
        SET
            status = 1,
            operator = ?,
            updated_at = ?
        WHERE
            thread_id = ?
    '''
    now = int(time.time())
    cursor.execute(sql_str, (operator, now, thread_id))
    return None


def reject(cursor, operator, reason, thread_id):
    sql_str = '''
        UPDATE
            approval_tasks
        SET
            status = 2,
            operator = ?,
            reject_reason = ?,
            updated_at = ?
        WHERE
            thread_id = ?
    '''
    now = int(time.time())
    cursor.execute(sql_str, (operator, reason, now, thread_id))
    return None
