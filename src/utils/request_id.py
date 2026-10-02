import uuid


def new_request_id() -> str:
    return uuid.uuid4().hex[:12]
