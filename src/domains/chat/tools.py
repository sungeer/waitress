from jsonschema import validate, ValidationError
from loguru import logger

from src.domains.chat import weather
from src.domains.chat.errors import UpstreamError
from src.utils import serial


weather_tool = {
    'type': 'function',
    'function': {
        'name': 'get_weather',
        'description': '查询指定经纬度的当前天气',
        'parameters': {
            'type': 'object',
            'properties': {
                'latitude': {
                    'type': 'number',
                    'minimum': -90,
                    'maximum': 90,
                    'description': '纬度',
                },
                'longitude': {
                    'type': 'number',
                    'minimum': -180,
                    'maximum': 180,
                    'description': '经度',
                },
            },
            'required': ['latitude', 'longitude'],
            'additionalProperties': False,
        },
    },
}

weather_tools = [weather_tool]
weather_parameters = weather_tool['function']['parameters']


async def execute(tool_call: dict) -> dict:
    function = tool_call.get('function')
    if not isinstance(function, dict):
        logger.error('tool call function is invalid, tool_call={}', tool_call)
        return {'error': 'invalid tool call'}

    name = function.get('name')
    if name != 'get_weather':
        logger.warning('unknown tool name={}', name)
        return {'error': f'unknown tool: {name}'}

    arguments = function.get('arguments')
    if not isinstance(arguments, str):
        logger.warning('tool arguments is not a str, name={}', name)
        return {'error': 'invalid arguments'}

    try:
        args = serial.from_json(arguments)
    except ValueError:
        logger.warning(
            'tool arguments json decode error, name={}, arguments={}',
            name, arguments
        )
        return {'error': 'invalid arguments json'}

    if not isinstance(args, dict):
        logger.warning('tool arguments is not an object, name={}', name)
        return {'error': 'arguments must be a JSON object'}

    try:
        validate(args, weather_parameters)
    except ValidationError as exc:
        logger.warning(
            'tool arguments validation failed, name={}, args={}, msg={}',
            name, args, exc.message
        )
        return {'error': f'invalid arguments: {exc.message}'}

    try:
        return await weather.fetch_current(args['latitude'], args['longitude'])
    except UpstreamError as exc:
        logger.exception('weather tool failed, args={}', args)
        return {'error': str(exc)}
