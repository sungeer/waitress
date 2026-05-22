def create_conversation(cursor, thread_id, title):
    sql_str = '''
        INSERT INTO conversations (thread_id, title, created_at)
        VALUES (%s, %s, NOW())
    '''
    cursor.execute(sql_str, (thread_id, title))


def get_conversation(cursor, thread_id):
    sql_str = '''
        SELECT
            id
        FROM
            conversations
        WHERE
            thread_id = %s
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
            conversation_id = %s
        ORDER BY id
    '''
    cursor.execute(sql_str, (conversation_id,))
    return [{'role': r['role'], 'content': r['content']} for r in cursor.fetchall()]


def insert_message(cursor, conversation_id, role, content):
    sql_str = '''
        INSERT INTO messages (conversation_id, role, content, created_at)
        VALUES (%s, %s, %s, NOW())
    '''
    cursor.execute(sql_str, (conversation_id, role, content))


# ========== 任务相关 ==========


def create_task(cursor, task_id, thread_id):
    sql_str = '''
        INSERT INTO tasks (task_id, thread_id, status, created_at)
        VALUES (%s, %s, 0, NOW())
    '''
    cursor.execute(sql_str, (task_id, thread_id))


def update_task_status(cursor, task_id, status):
    sql_str = 'UPDATE tasks SET status = %s WHERE task_id = %s'
    cursor.execute(sql_str, (status, task_id))


def set_task_failed(cursor, task_id, error_message):
    sql_str = 'UPDATE tasks SET status = 3, error_message = %s WHERE task_id = %s'
    cursor.execute(sql_str, (error_message, task_id))


def get_task(cursor, task_id):
    sql_str = '''
        SELECT
            task_id, thread_id, status, error_message, created_at, updated_at
        FROM
            tasks
        WHERE
            task_id = %s
    '''
    cursor.execute(sql_str, (task_id,))
    return cursor.fetchone()


def insert_result(cursor, task_id, content):
    sql_str = '''
        INSERT INTO task_results (task_id, content, created_at)
        VALUES (%s, %s, NOW())
    '''
    cursor.execute(sql_str, (task_id, content))


def get_result(cursor, task_id):
    sql_str = '''
        SELECT
            content, created_at
        FROM
            task_results
        WHERE
            task_id = %s
    '''
    cursor.execute(sql_str, (task_id,))
    return cursor.fetchone()
