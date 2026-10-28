from loguru import logger

from src import settings
from src.core.http_client import httpx, HTTPError
from src.domains.chat.errors import UpstreamError


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
    return content
