def check_db_conn(conn):
    sql = 'SELECT 1'
    conn.execute(sql)
    return None
