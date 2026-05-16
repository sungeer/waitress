def create_conversation(conn, thread_id, title):
    sql_str = '''
        INSERT INTO conversation (thread_id, title)
        VALUES (?, ?)
    '''
    conn.execute(sql_str, (thread_id, title))
    row_id = conn.lastrowid
    return row_id
