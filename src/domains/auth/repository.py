def get_user_by_ref_id(cursor, ref_id):
    sql_str = '''
        SELECT
            id, ref_id, username, display_name, email
        FROM
            users
        WHERE
            ref_id = %s
    '''
    cursor.execute(sql_str, (ref_id,))
    return cursor.fetchone()


def create_user(cursor, ref_id, username, display_name, email):
    sql_str = '''
        INSERT INTO users (
            ref_id, username, display_name, email, created_at
        ) VALUES (%s, %s, %s, %s, NOW())
    '''
    cursor.execute(sql_str, (ref_id, username, display_name, email))
    return cursor.lastrowid


def get_user_by_id(cursor, user_id):
    sql_str = '''
        SELECT
            id, ref_id, username, display_name, email
        FROM
            users
        WHERE
            id = %s
    '''
    cursor.execute(sql_str, (user_id,))
    return cursor.fetchone()


def update_last_login(cursor, user_id):
    sql_str = '''
        UPDATE
            users
        SET
            last_login_at = NOW()
        WHERE
            id = %s
    '''
    cursor.execute(sql_str, (user_id,))
    return None
