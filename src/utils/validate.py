from json import JSONDecodeError

from loguru import logger
from pydantic import BaseModel, ValidationError

from src.core.exceptions import BadRequestError


async def require_body(request):
    try:
        data = await request.json()
    except JSONDecodeError:
        raise BadRequestError('request body is not valid JSON')
    if not isinstance(data, dict):
        raise BadRequestError('request body must be a JSON object')
    return data


def require_int(data, key):
    value = data.get(key)
    if not isinstance(value, int) or isinstance(value, bool):
        raise BadRequestError(f'{key} must be an integer')
    return value


def optional_int(data, key, default):
    value = data.get(key)
    if value is None:
        return default
    if not isinstance(value, int) or isinstance(value, bool):
        raise BadRequestError(f'{key} must be an integer')
    return value


def require_str(data, key):
    value = data.get(key)
    if not isinstance(value, str) or not value.strip():
        raise BadRequestError(f'{key} cannot be empty')
    return value


def optional_str(data, key, default=None):
    value = data.get(key)
    if value is None:
        return default
    if not isinstance(value, str) or not value.strip():
        raise BadRequestError(f'{key} cannot be empty')
    return value


def require_model(data: dict, model: type[BaseModel]):
    try:
        payload = model.model_validate(data)
    except ValidationError as e:
        logger.warning(
            'request body validation failed model={} detail={}',
            model.__name__, e
        )
        raise BadRequestError('bad request')
    return payload
