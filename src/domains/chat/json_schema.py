from loguru import logger
from jsonschema import validate, ValidationError

from src.domains.chat.errors import UpstreamError


structured_schema = {
    'type': 'object',
    'properties': {
        'customer_name': {'type': 'string'},
        'phone': {'type': 'string'},
        'items': {
            'type': 'array',
            'minItems': 1,
            'items': {
                'type': 'object',
                'properties': {
                    'product_name': {'type': 'string'},
                    'quantity': {'type': 'integer'},
                    'unit_price': {'type': 'number'},
                },
                'required': ['product_name', 'quantity', 'unit_price'],
            },
        },
        'total_amount': {'type': 'number'},
        'is_urgent': {'type': 'boolean'},
    },
    'required': ['customer_name', 'phone', 'items', 'total_amount', 'is_urgent'],
}


def validate_struct(raw, schema):
    try:
        validate(raw, schema)
    except ValidationError as e:
        logger.error(
            'struct validation failed, path={}, message={}, raw={}',
            list(e.absolute_path), e.message, raw
        )
        raise UpstreamError('struct validation failed')
