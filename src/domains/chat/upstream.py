from loguru import logger

from src import settings
from src.core.http_client import httpx, HTTPError
from src.domains.chat.errors import UpstreamError
from src.domains.chat.prompts import structured_system_prompt
from src.domains.chat import json_schema
from src.utils import serial


async def complete() -> str:
    url = 'https://api.deepseek.com/chat/completions'

    headers = {
        'Authorization': f'Bearer {settings.LLM_KEY}',
        'Content-Type': 'application/json'
    }

    payload = {
        'model': settings.LLM_MODEL,
        'messages': [
            {'role': 'system', 'content': 'You are a helpful assistant.'},
            {'role': 'user', 'content': 'Hello!'}
        ],
        'stream': False,
        'thinking': {'type': 'disabled'}
    }

    client = httpx.get_client()
    try:
        response = await client.post(url, headers=headers, json=payload)
        response.raise_for_status()
        data = response.json()
    except (HTTPError, ValueError):
        logger.exception(
            'llm request failed, url={}, payload={}',
            url, payload
        )
        raise UpstreamError('llm request failed')

    logger.info('llm response data={}', data)

    if not isinstance(data, dict):
        logger.error(
            'llm response data is not a dict, type={}, data={}',
            type(data).__name__, data
        )
        raise UpstreamError('data type is incorrect')

    choices = data.get('choices')
    if not isinstance(choices, list):
        logger.error(
            'llm response choices is not a list, type={}, choices={}',
            type(choices).__name__, choices
        )
        raise UpstreamError('choices type is incorrect')

    if not choices:
        logger.error('llm response choices is empty')
        raise UpstreamError('choices is empty')

    choice, *_ = choices
    if not isinstance(choice, dict):
        logger.error(
            'llm response choice is not a dict, type={}, choice={}',
            type(choice).__name__, choice
        )
        raise UpstreamError('choice type is incorrect')

    finish_reason = choice.get('finish_reason')
    if finish_reason != 'stop':
        logger.error(
            'llm response finish_reason is not stop, finish_reason={}',
            finish_reason
        )
        raise UpstreamError('finish_reason is not stop')

    message = choice.get('message')
    if not isinstance(message, dict):
        logger.error(
            'llm response message is not a dict, type={}, message={}',
            type(message).__name__, message
        )
        raise UpstreamError('message type is incorrect')

    content = message.get('content')
    if not isinstance(content, str):
        logger.error(
            'llm response content is not a str, type={}, content={}',
            type(content).__name__, content
        )
        raise UpstreamError('content type is incorrect')

    if not content:
        logger.error(
            'llm response content is empty, finish_reason={}',
            finish_reason
        )
        raise UpstreamError('content is empty')
    return content


async def structured():
    url = 'https://api.deepseek.com/chat/completions'

    headers = {
        'Authorization': f'Bearer {settings.LLM_KEY}',
        'Content-Type': 'application/json'
    }

    user_msg = (
        '你好，我叫张三，电话是13800138000。'
        '我要订2台iPhone 15 Pro Max，单价8999元；'
        '再加1个AirPods Pro，单价1899元。'
        '总共应该是19897元吧？急用，麻烦快点发货！'
    )

    payload = {
        'model': settings.LLM_MODEL,
        'messages': [
            {'role': 'system', 'content': structured_system_prompt},
            {'role': 'user', 'content': user_msg}
        ],
        'max_tokens': 1024,  # 防止 JSON 字符串被中途截断
        'stream': False,
        'thinking': {'type': 'enabled'},
        'reasoning_effort': 'low',
        'response_format': {'type': 'json_object'},
    }

    client = httpx.get_client()
    try:
        response = await client.post(url, headers=headers, json=payload)
        response.raise_for_status()
        data = response.json()
    except (HTTPError, ValueError):
        logger.exception(
            'llm request failed, url={}, payload={}',
            url, payload
        )
        raise UpstreamError('llm request failed')

    logger.info('llm response data={}', data)

    if not isinstance(data, dict):
        logger.error(
            'llm response data is not a dict, type={}, data={}',
            type(data).__name__, data
        )
        raise UpstreamError('data type is incorrect')

    choices = data.get('choices')
    if not isinstance(choices, list):
        logger.error(
            'llm response choices is not a list, type={}, choices={}',
            type(choices).__name__, choices
        )
        raise UpstreamError('choices type is incorrect')

    if not choices:
        logger.error('llm response choices is empty')
        raise UpstreamError('choices is empty')

    choice, *_ = choices
    if not isinstance(choice, dict):
        logger.error(
            'llm response choice is not a dict, type={}, choice={}',
            type(choice).__name__, choice
        )
        raise UpstreamError('choice type is incorrect')

    finish_reason = choice.get('finish_reason')
    if finish_reason != 'stop':
        logger.error(
            'llm response finish_reason is not stop, finish_reason={}, max_tokens={}',
            finish_reason, payload['max_tokens']
        )
        raise UpstreamError('finish_reason is not stop')

    message = choice.get('message')
    if not isinstance(message, dict):
        logger.error(
            'llm response message is not a dict, type={}, message={}',
            type(message).__name__, message
        )
        raise UpstreamError('message type is incorrect')

    content = message.get('content')
    if not isinstance(content, str):
        logger.error(
            'llm response content is not a str, type={}, content={}',
            type(content).__name__, content
        )
        raise UpstreamError('content type is incorrect')

    if not content:
        logger.error(
            'llm response content is empty, finish_reason={}',
            finish_reason
        )
        raise UpstreamError('content is empty')

    try:
        parsed = serial.from_json(content)
    except ValueError:
        logger.exception('json decode error, content={}', content)
        raise UpstreamError('json decode error')

    structured_schema = json_schema.structured_schema
    json_schema.validate_struct(parsed, structured_schema)
    return parsed


def _validate_tool_call(tool_call):
    if not isinstance(tool_call, dict):
        logger.error(
            'llm tool_call is not a dict, type={}, tool_call={}',
            type(tool_call).__name__, tool_call
        )
        raise UpstreamError('tool_call type is incorrect')

    call_id = tool_call.get('id')
    if not isinstance(call_id, str) or not call_id:
        logger.error('llm tool_call id is invalid, tool_call={}', tool_call)
        raise UpstreamError('tool_call id is invalid')

    if tool_call.get('type') != 'function':
        logger.error('llm tool_call type is unsupported, tool_call={}', tool_call)
        raise UpstreamError('tool_call type is unsupported')

    function = tool_call.get('function')
    if not isinstance(function, dict):
        logger.error(
            'llm tool_call function is not a dict, tool_call={}', tool_call
        )
        raise UpstreamError('tool_call function is incorrect')

    name = function.get('name')
    if not isinstance(name, str) or not name:
        logger.error('llm tool_call name is invalid, tool_call={}', tool_call)
        raise UpstreamError('tool_call name is invalid')

    arguments = function.get('arguments')
    if not isinstance(arguments, str):
        logger.error(
            'llm tool_call arguments is not a str, tool_call={}', tool_call
        )
        raise UpstreamError('tool_call arguments is incorrect')


async def chat(messages, tools=None, tool_choice=None):
    url = 'https://api.deepseek.com/chat/completions'

    headers = {
        'Authorization': f'Bearer {settings.LLM_KEY}',
        'Content-Type': 'application/json'
    }

    payload = {
        'model': settings.LLM_MODEL,
        'messages': messages,
        'max_tokens': 1024,
        'stream': False,
        'thinking': {'type': 'enabled'},
        'reasoning_effort': 'low',
    }
    if tools is not None:
        payload['tools'] = tools
    if tool_choice is not None:
        payload['tool_choice'] = tool_choice

    client = httpx.get_client()
    try:
        response = await client.post(url, headers=headers, json=payload)
        response.raise_for_status()
        data = response.json()
    except (HTTPError, ValueError):
        logger.exception(
            'llm request failed, url={}, payload={}',
            url, payload
        )
        raise UpstreamError('llm request failed')

    logger.info('llm response data={}', data)

    if not isinstance(data, dict):
        logger.error(
            'llm response data is not a dict, type={}, data={}',
            type(data).__name__, data
        )
        raise UpstreamError('data type is incorrect')

    choices = data.get('choices')
    if not isinstance(choices, list):
        logger.error(
            'llm response choices is not a list, type={}, choices={}',
            type(choices).__name__, choices
        )
        raise UpstreamError('choices type is incorrect')

    if not choices:
        logger.error('llm response choices is empty')
        raise UpstreamError('choices is empty')

    choice, *_ = choices
    if not isinstance(choice, dict):
        logger.error(
            'llm response choice is not a dict, type={}, choice={}',
            type(choice).__name__, choice
        )
        raise UpstreamError('choice type is incorrect')

    finish_reason = choice.get('finish_reason')
    if finish_reason not in ('stop', 'tool_calls'):
        logger.error(
            'llm response finish_reason is unsupported, finish_reason={}',
            finish_reason
        )
        raise UpstreamError('finish_reason is unsupported')

    message = choice.get('message')
    if not isinstance(message, dict):
        logger.error(
            'llm response message is not a dict, type={}, message={}',
            type(message).__name__, message
        )
        raise UpstreamError('message type is incorrect')

    if finish_reason == 'stop':
        content = message.get('content')
        if not isinstance(content, str):
            logger.error(
                'llm response content is not a str, type={}, content={}',
                type(content).__name__, content
            )
            raise UpstreamError('content type is incorrect')
        if not content:
            logger.error('llm response content is empty')
            raise UpstreamError('content is empty')
    else:
        tool_calls = message.get('tool_calls')
        if not isinstance(tool_calls, list):
            logger.error(
                'llm response tool_calls is not a list, type={}, tool_calls={}',
                type(tool_calls).__name__, tool_calls
            )
            raise UpstreamError('tool_calls type is incorrect')
        if not tool_calls:
            logger.error('llm response tool_calls is empty')
            raise UpstreamError('tool_calls is empty')
        for tool_call in tool_calls:
            _validate_tool_call(tool_call)

    return choice
