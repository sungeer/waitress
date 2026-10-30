from json import JSONDecodeError

from loguru import logger
from jsonschema import validate, ValidationError

from src.utils.exceptions import ParamError
from src.domains.chat.errors import UpstreamError


async def require_body(request):
    try:
        data = await request.json()
    except JSONDecodeError:
        raise ParamError('request body is not valid JSON')
    if not isinstance(data, dict):
        raise ParamError('request body must be a JSON object')
    return data


def validated_struct(raw, schema):
    try:
        validate(raw, schema)
    except ValidationError as e:
        logger.error(
            'struct validation failed, path={}, message={}, raw={}',
            list(e.absolute_path), e.message, raw
        )
        raise UpstreamError('struct validation failed')
