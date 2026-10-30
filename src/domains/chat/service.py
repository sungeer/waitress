import asyncio
import random

from src.domains.chat import upstream
from src.domains.chat import tools
from src.domains.chat.errors import UpstreamError
from src.domains.chat.prompts import react_system_prompt
from src.utils import serial
from src.utils.exceptions import UpstreamUnavailableError


async def stream_chunks():
    full_text = (
        '人工智能正在改变我们的世界，从语音识别到图像生成，'
        '从自动驾驶到智能推荐，它渗透进了生活的方方面面。'
        '未来已来，只是尚未均匀分布。'
    )

    pos = 0
    total = len(full_text)

    while pos < total:
        size = random.randint(1, 7)
        chunk = full_text[pos:pos + size]
        pos += size

        yield serial.to_json({'delta': chunk}) + '\n'

        await asyncio.sleep(random.uniform(0.1, 0.5))


async def ask() -> str:
    try:
        return await upstream.complete()
    except UpstreamError as exc:
        raise UpstreamUnavailableError() from exc


async def structured():
    try:
        return await upstream.structured()
    except UpstreamError as exc:
        raise UpstreamUnavailableError() from exc


MAX_ROUNDS = 3
MAX_TOOL_CALLS = 3


async def react(question: str, latitude: float, longitude: float) -> str:
    messages = [
        {'role': 'system', 'content': react_system_prompt},
        {
            'role': 'user',
            'content': (
                f'问题：{question}\n'
                f'可用坐标：latitude={latitude}, longitude={longitude}'
            ),
        },
    ]
    tool_calls_used = 0

    try:
        for _ in range(MAX_ROUNDS):
            choice = await upstream.chat(
                messages,
                tools=tools.weather_tools,
            )
            message = choice['message']

            if choice['finish_reason'] == 'stop':
                return message['content']

            messages.append(message)

            for tool_call in message['tool_calls']:
                if tool_calls_used >= MAX_TOOL_CALLS:
                    result = {'error': 'tool call limit exceeded'}
                else:
                    result = await tools.execute(tool_call)
                    tool_calls_used += 1

                messages.append({
                    'role': 'tool',
                    'tool_call_id': tool_call['id'],
                    'content': serial.to_json(result),
                })

            if tool_calls_used >= MAX_TOOL_CALLS:
                break

        messages.append({
            'role': 'user',
            'content': '已达到工具调用上限，不要再调用工具，直接基于以上信息用中文回答。',
        })
        choice = await upstream.chat(
            messages,
            tools=tools.weather_tools,
            tool_choice='none',
        )
        return choice['message']['content']
    except UpstreamError as exc:
        raise UpstreamUnavailableError() from exc
