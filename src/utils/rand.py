import uuid


def gen_token(n: int = 18) -> str:
    return uuid.uuid4().hex[:n]
