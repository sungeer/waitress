import json
from datetime import datetime

from sqlalchemy import text


def _payload_to_dict(payload):
    if isinstance(payload, dict):
        return payload
    return json.loads(payload)


def get(conn, cell: str) -> dict | None:
    sql = text('''
        SELECT
            cell, payload, fetched_at,
            consecutive_failures, last_error,
            next_retry_at
        FROM
            weather_snapshots
        WHERE
            cell = :cell
    ''')

    params = {
        'cell': cell
    }

    row = conn.execute(sql, params).mappings().first()  # RowMapping | None

    if row is None:
        return None

    data = dict(row)
    data['payload'] = _payload_to_dict(data['payload'])
    return data


def insert(conn, cell: str, payload: dict, fetched_at: datetime):
    sql = text('''
        INSERT INTO weather_snapshots
            (cell, payload, fetched_at, consecutive_failures)
        VALUES
            (:cell, CAST(:payload AS JSON), :fetched_at, 0)
    ''')

    params = {
        'cell': cell,
        'payload': json.dumps(payload, ensure_ascii=False),
        'fetched_at': fetched_at,
    }

    conn.execute(sql, params)


def update_success(conn, cell: str, payload: dict, fetched_at: datetime) -> int:
    # 成功后清零失败计数与退避时间
    sql = text('''
        UPDATE
            weather_snapshots
        SET
            payload = CAST(:payload AS JSON),
            fetched_at = :fetched_at,
            consecutive_failures = 0,
            last_error = NULL,
            next_retry_at = NULL
        WHERE
            cell = :cell
    ''')

    params = {
        'payload': json.dumps(payload, ensure_ascii=False),
        'fetched_at': fetched_at,
        'cell': cell,
    }

    result = conn.execute(sql, params)

    return result.rowcount


def mark_failure(conn, cell: str, error: str, next_retry_at: datetime) -> int:
    sql = text('''
        UPDATE
            weather_snapshots
        SET
            consecutive_failures = consecutive_failures + 1,
            last_error = :error,
            next_retry_at = :next_retry_at
        WHERE
            cell = :cell
    ''')

    params = {
        'error': error[:250],
        'next_retry_at': next_retry_at,
        'cell': cell,
    }

    result = conn.execute(sql, params)

    return result.rowcount
