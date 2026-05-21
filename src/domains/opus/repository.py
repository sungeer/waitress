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
