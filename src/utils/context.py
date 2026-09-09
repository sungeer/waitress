import uuid


def new_request_id() -> str:
    request_id = uuid.uuid4().hex[:16]  # 'd8961c3c4f884505'
    return request_id
