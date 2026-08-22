from src.core.exceptions import BadRequestError


def require_int(data, key):
    value = data.get(key)
    if not isinstance(value, int) or isinstance(value, bool):
        raise BadRequestError(f'{key} 必须是整数')
    return value


def optional_int(data, key, default):
    value = data.get(key)
    if value is None:
        return default
    if not isinstance(value, int) or isinstance(value, bool):
        raise BadRequestError(f'{key} 必须是整数')
    return value


def require_str(data, key):
    value = data.get(key)
    if not isinstance(value, str) or not value.strip():
        raise BadRequestError(f'{key} 不能为空')
    return value


def optional_str(data, key, default=None):
    value = data.get(key)
    if value is None:
        return default
    if not isinstance(value, str) or not value.strip():
        raise BadRequestError(f'{key} 不能为空')
    return value
