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
    except (HTTPError, ValueError) as exc:
        raise UpstreamError(f'llm completion failed: {exc}') from exc

    logger.info('llm response data={}', data)

    try:
        content = data['choices'][0]['message']['content']
    except (KeyError, IndexError, TypeError) as exc:
        raise UpstreamError('unexpected llm payload') from exc

    if not isinstance(content, str):
        raise UpstreamError('unexpected llm payload')
    return content
