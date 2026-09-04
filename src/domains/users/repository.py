from sqlalchemy import text
from sqlalchemy.exc import IntegrityError

from src.core.exceptions import DuplicateKeyError


def query_one(cursor, user_id):
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

    result = cursor.execute(sql, params)

    row = result.mappings().first()  # RowMapping | None
    # row = result.mappings().one()  # 没有或多于一条都会抛异常

    return dict(row) if row else None


def query_many(cursor, limit):
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

    result = cursor.execute(sql, params)
    rows = result.mappings().all()  # list[RowMapping]

    return [dict(r) for r in rows]


def insert_user(cursor, username, display_name, email):
    sql = text('''
        INSERT INTO users(username, display_name, email)
        VALUES (:username, :display_name, :email)
    ''')

    params = {
        'username': username,
        'display_name': display_name,
        'email': email,
    }

    try:
        result = cursor.execute(sql, params)
    except IntegrityError as exc:
        raise DuplicateKeyError from exc

    return result.lastrowid


def update_display_name(cursor, new_display_name, user_id):
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

    result = cursor.execute(sql, params)

    return result.rowcount


def username_exists(cursor, username):
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

    row = cursor.execute(sql, params).mappings().first()

    return row is not None


def email_exists(cursor, email):
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

    row = cursor.execute(sql, params).mappings().first()

    return row is not None


def delete_user(cursor, user_id):
    sql = text('''
        DELETE FROM
            users
        WHERE
            id = :id
    ''')

    params = {
        'id': user_id
    }

    result = cursor.execute(sql, params)

    return result.rowcount
