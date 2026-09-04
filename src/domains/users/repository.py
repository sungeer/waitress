from sqlalchemy import text


def query_one(conn, user_id: int) -> dict | None:
    sql = text('''
        SELECT
            id, username, display_name, email
        FROM
            users
        WHERE
            id = :id
    ''')

    params = {
        'id': user_id
    }

    result = conn.execute(sql, params)

    row = result.mappings().first()  # RowMapping | None
    # row = result.mappings().one()  # 没有或多于一条都会抛异常

    return dict(row) if row else None


def query_many(conn, limit: int) -> list[dict]:
    sql = text('''
        SELECT
            id, username, display_name, email
        FROM
            users
        ORDER BY id
        LIMIT :limit
    ''')

    params = {
        'limit': limit
    }

    result = conn.execute(sql, params)
    rows = result.mappings().all()  # list[RowMapping]

    return [dict(r) for r in rows]


def insert_user(conn, username: str, display_name: str | None, email: str) -> int:
    sql = text('''
        INSERT INTO users(username, display_name, email)
        VALUES (:username, :display_name, :email)
    ''')

    params = {
        'username': username,
        'display_name': display_name,
        'email': email,
    }

    result = conn.execute(sql, params)

    return result.lastrowid


def update_display_name(conn, new_display_name: str, user_id: int) -> int:
    sql = text('''
        UPDATE
            users
        SET
            display_name = :display_name
        WHERE
            id = :id
    ''')

    params = {
        'display_name': new_display_name,
        'id': user_id
    }

    result = conn.execute(sql, params)

    return result.rowcount


def username_exists(conn, username: str) -> bool:
    sql = text('''
        SELECT 1
        FROM
            users
        WHERE
            username = :username
    ''')

    params = {
        'username': username
    }

    row = conn.execute(sql, params).mappings().first()

    return row is not None


def email_exists(conn, email: str) -> bool:
    sql = text('''
        SELECT 1
        FROM
            users
        WHERE
            email = :email
    ''')

    params = {
        'email': email
    }

    row = conn.execute(sql, params).mappings().first()

    return row is not None


def delete_user(conn, user_id: int) -> int:
    sql = text('''
        DELETE FROM
            users
        WHERE
            id = :id
    ''')

    params = {
        'id': user_id
    }

    result = conn.execute(sql, params)

    return result.rowcount
