def check_db_conn(cursor):
    sql_str = 'SELECT 1'
    cursor.execute(sql_str)
    return None
