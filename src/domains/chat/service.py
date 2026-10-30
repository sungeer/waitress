import asyncio
import random

from src.domains.chat import upstream
from src.domains.chat.errors import UpstreamError
from src.utils import serial
from src.utils.exceptions import BusinessError


async def generator():
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
        raise BusinessError('upstream data source unavailable') from exc


async def structured():
    try:
        return await upstream.structured()
    except UpstreamError as exc:
        raise BusinessError('upstream data source unavailable') from exc
