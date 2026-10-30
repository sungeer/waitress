import math
from json import JSONDecodeError

from src.utils.exceptions import ParamError


async def require_body(request):
    try:
        data = await request.json()
    except JSONDecodeError:
        raise ParamError('request body is not valid JSON')
    if not isinstance(data, dict):
        raise ParamError('request body must be a JSON object')
    return data


def require_int(data, key):
    value = data.get(key)
    if value is None:
        raise ParamError(f'{key} is required')
    if not isinstance(value, int) or isinstance(value, bool):
        raise ParamError(f'{key} must be an integer')
    return value


def require_str(data, key):
    value = data.get(key)
    if value is None:
        raise ParamError(f'{key} is required')
    if not isinstance(value, str):
        raise ParamError(f'{key} must be a string')
    if not value.strip():
        raise ParamError(f'{key} cannot be empty')
    return value


def require_number(data, key, minimum=None, maximum=None):
    value = data.get(key)
    if value is None:
        raise ParamError(f'{key} is required')
    if not isinstance(value, (int, float)) or isinstance(value, bool):
        raise ParamError(f'{key} must be a number')
    if not math.isfinite(value):
        raise ParamError(f'{key} must be finite')
    if minimum is not None and value < minimum:
        raise ParamError(f'{key} must be >= {minimum}')
    if maximum is not None and value > maximum:
        raise ParamError(f'{key} must be <= {maximum}')
    return float(value)
