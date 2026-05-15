def find_by_staff_id(conn, staff_id: str):
    sql = 'SELECT id, staff_id, username, display_name, email, department, is_active FROM user WHERE staff_id = %s'
    conn.execute(sql, (staff_id,))
    return conn.fetchone()


def create_user(conn, user_data: dict) -> int:
    sql = '''
        INSERT INTO user (staff_id, username, display_name, email, department)
        VALUES (%(staff_id)s, %(username)s, %(display_name)s, %(email)s, %(department)s)
    '''
    conn.execute(sql, user_data)
    return conn.lastrowid
