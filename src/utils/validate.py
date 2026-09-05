from json import JSONDecodeError

from loguru import logger
from pydantic import BaseModel, ValidationError

from src.core.codes import BizCode
from src.core.exceptions import BusinessError


async def require_body(request):
    try:
        data = await request.json()
    except JSONDecodeError:
        raise BusinessError(BizCode.PARAM_ERROR, 'request body is not valid JSON')
    if not isinstance(data, dict):
        raise BusinessError(BizCode.PARAM_TYPE_ERROR, 'request body must be a JSON object')
    return data


def _extract_invalid_fields(validation_error: ValidationError) -> list[str]:
    invalid_fields = []
    for error in validation_error.errors():
        # 只提取有问题的字段路径
        field_path = '.'.join(str(loc) for loc in error['loc'])
        if field_path:
            invalid_fields.append(field_path)

    return list(set(invalid_fields))


def require_model(data: dict, model: type[BaseModel]):
    try:
        payload = model.model_validate(data)
    except ValidationError as e:
        logger.warning(
            'request body validation failed model={} detail={}',
            model.__name__, e
        )
        invalid_fields = _extract_invalid_fields(e)
        raise BusinessError(BizCode.PARAM_ERROR, f'bad request: {invalid_fields}')
    return payload


def require_int(data, key):
    value = data.get(key)
    if value is None:
        raise BusinessError(BizCode.PARAM_MISSING, f'{key} is required')
    if not isinstance(value, int) or isinstance(value, bool):
        raise BusinessError(BizCode.PARAM_TYPE_ERROR, f'{key} must be an integer')
    return value


def optional_int(data, key, default):
    value = data.get(key)
    if value is None:
        return default
    if not isinstance(value, int) or isinstance(value, bool):
        raise BusinessError(BizCode.PARAM_TYPE_ERROR, f'{key} must be an integer')
    return value


def require_str(data, key):
    value = data.get(key)
    if value is None:
        raise BusinessError(BizCode.PARAM_MISSING, f'{key} is required')
    if not isinstance(value, str):
        raise BusinessError(BizCode.PARAM_TYPE_ERROR, f'{key} must be a string')
    if not value.strip():
        raise BusinessError(BizCode.PARAM_ERROR, f'{key} cannot be empty')
    return value


def optional_str(data, key, default=None):
    value = data.get(key)
    if value is None:
        return default
    if not isinstance(value, str):
        raise BusinessError(BizCode.PARAM_TYPE_ERROR, f'{key} must be a string')
    if not value.strip():
        raise BusinessError(BizCode.PARAM_ERROR, f'{key} cannot be empty')
    return value


def require_float_in(data, key, low, high):
    # 数值(含字符串"39.9")在 [low, high] 区间内才放行，返回 float
    value = data.get(key)
    if value is None:
        raise BusinessError(BizCode.PARAM_MISSING, f'{key} is required')
    try:
        num = float(value)
    except (TypeError, ValueError):
        raise BusinessError(BizCode.PARAM_TYPE_ERROR, f'{key} must be a number')
    if not low <= num <= high:
        raise BusinessError(BizCode.PARAM_OUT_OF_RANGE, f'{key} out of range [{low}, {high}]')
    return num
