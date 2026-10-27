from starlette.responses import StreamingResponse
from loguru import logger

from src.domains.chat import service
from src import settings
from src.core.response import ok
from src.core.http_client import httpx
from src.utils import serial


async def stream(request):
    return StreamingResponse(
        service.generator(),
        media_type='application/x-ndjson',
        headers={
            'Cache-Control': 'no-cache',
            'X-Accel-Buffering': 'no',
        }
    )


async def ask(request):
    system_prompt = 'You are a helpful assistant.'

    api_key = settings.LLM_KEY

    url = 'https://api.deepseek.com/chat/completions'

    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json'
    }

    user_prompt = 'Hello!'

    payload = {
        'model': settings.LLM_MODEL,
        'messages': [
            {'role': 'system', 'content': system_prompt},
            {'role': 'user', 'content': user_prompt}
        ],
        'stream': False,
        'thinking': {'type': 'disabled'}
    }

    client = httpx.get_client()
    response = await client.post(url, headers=headers, json=payload)
    response.raise_for_status()  # 检查 HTTP 错误
    data = response.json()

    logger.info('llm response data={}', data)

    content = data['choices'][0]['message']['content']
    return ok(content)
