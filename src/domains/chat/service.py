import asyncio
import random

from loguru import logger

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


async def react(question: str) -> str:
    messages = [
        {'role': 'system', 'content': react_system_prompt},
        {'role': 'user', 'content': question},
    ]
    tool_calls_used = 0

    max_rounds = 3
    max_tool_calls = 3

    try:
        for round_no in range(1, max_rounds + 1):
            logger.info('[round {}] llm call', round_no)
            choice = await upstream.chat(
                messages,
                tools=tools.weather_tools,
            )
            message = choice['message']
            logger.info('[round {}] finish_reason={}', round_no, choice['finish_reason'])

            if choice['finish_reason'] == 'stop':
                logger.info('[round {}] answer directly', round_no)
                return message['content']

            messages.append(message)

            for tool_call in message['tool_calls']:
                function = tool_call['function']
                if tool_calls_used >= max_tool_calls:
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

            if tool_calls_used >= max_tool_calls:
                logger.warning('[round {}] tool call limit reached, break', round_no)
                break

        messages.append({
            'role': 'user',
            'content': '已达到工具调用上限，不要再调用工具，直接基于以上信息用中文回答。',
        })
        logger.warning('tool call limit or rounds exhausted, force final answer')
        choice = await upstream.chat(
            messages,
            tools=tools.weather_tools,
            tool_choice='none',
        )
        return choice['message']['content']
    except UpstreamError as exc:
        raise UpstreamUnavailableError() from exc
