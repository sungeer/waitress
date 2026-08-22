from sqlalchemy import text


def query_one(cursor, user_id):
    sql = text('''
        SELECT id, name, age
        FROM user
        WHERE id = :id
    ''')

    params = {
        'id': user_id
    }

    result = cursor.execute(sql, params)

    row = result.mappings().first()  # RowMapping | None
    # row = result.mappings().one()  # 没有或多于一条都会抛异常

    return dict(row) if row else None


def query_many(cursor, min_age, limit):
    sql = text('''
        SELECT id, name, age
        FROM user
        WHERE age >= :min_age
        ORDER BY id
        LIMIT :limit
    ''')

    params = {
        'min_age': min_age,
        'limit': limit
    }

    result = cursor.execute(sql, params
                            )
    rows = result.mappings().all()  # list[RowMapping]

    return [dict(r) for r in rows]


def insert_user(cursor, name, age):
    sql = text('INSERT INTO user(name, age) VALUES (:name, :age)')

    params = {
        'name': name,
        'age': age
    }

    result = cursor.execute(sql, params)

    return result.rowcount, result.lastrowid


def update_user_name(cursor, new_name, user_id):
    sql = text('UPDATE user SET name = :name WHERE id = :id')

    params = {
        'name': new_name,
        'id': user_id
    }

    result = cursor.execute(sql, params)

    return result.rowcount


def delete_user(cursor, user_id):
    sql = text('DELETE FROM user WHERE id = :id')

    params = {
        'id': user_id
    }

    result = cursor.execute(sql, params)

    return result.rowcount