import time


def start_cancel(cursor, thread_id, approver_id, content, order_id, amount, risk_level):
    sql_str = '''
        INSERT INTO approval_tasks (
            thread_id, approver_id, content, order_id, amount,
            risk_level, status, created_at, updated_at
        ) VALUES (?, ?, ?, ?, ?, ?, 0, ?, ?) 
    '''
    now = int(time.time())
    params = (thread_id, approver_id, content, order_id, amount, risk_level, now, now)
    cursor.execute(sql_str, params)
    return None


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
