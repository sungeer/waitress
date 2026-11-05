import asyncio
import random

from loguru import logger

from src.domains.chat import upstream
from src.domains.chat import tools
from src.domains.chat.budget import MAX_ROUNDS
from src.domains.chat.budget import MAX_TOOL_CALLS
from src.domains.chat.errors import ReactLoopExhaustedError
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


async def react(question: str) -> str:
    messages = [
        {'role': 'system', 'content': react_system_prompt},
        {'role': 'user', 'content': question},
    ]
    tool_calls_used = 0

    try:
        for round_no in range(1, MAX_ROUNDS + 1):
            logger.info('[round {}] llm call', round_no)
            finish_reason, message = await upstream.chat(
                messages,
                tools=tools.weather_tools,
            )
            logger.info('[round {}] finish_reason={}', round_no, finish_reason)

            if finish_reason == upstream.FINISH_REASON_STOP:
                return message['content']

            messages.append({
                'role': 'assistant',
                'content': message.get('content'),
                'tool_calls': message['tool_calls'],
            })

            for tool_call in message['tool_calls']:
                function = tool_call['function']
                if tool_calls_used >= MAX_TOOL_CALLS:
                    logger.warning(
                        '[round {}] tool call limit exceeded, skip name={}',
                        round_no, function['name']
                    )
                    result = {'error': 'tool call limit exceeded'}
                else:
                    logger.info(
                        '[round {}] tool call name={} args={}',
                        round_no, function['name'], function['arguments']
                    )
                    result = await tools.execute(tool_call)
                    tool_calls_used += 1

                logger.info('[round {}] tool result={}', round_no, serial.to_json(result))

                messages.append({
                    'role': 'tool',
                    'tool_call_id': tool_call['id'],
                    'content': serial.to_json(result),
                })

            if tool_calls_used >= MAX_TOOL_CALLS:
                break
    except UpstreamError as exc:
        raise UpstreamUnavailableError() from exc

    logger.error(
        'react loop exhausted, rounds={} tool_calls={}',
        round_no, tool_calls_used
    )
    raise ReactLoopExhaustedError(
        f'rounds={round_no} tool_calls={tool_calls_used}'
    )
