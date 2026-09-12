import uuid


def new_request_id() -> str:
    # 'd8961c3c4f884505'
    return uuid.uuid4().hex[:16]
