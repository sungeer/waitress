import asyncio
import random

from src.utils import serial

FULL_TEXT = (
    '人工智能正在改变我们的世界，从语音识别到图像生成，'
    '从自动驾驶到智能推荐，它渗透进了生活的方方面面。'
    '未来已来，只是尚未均匀分布。'
)


async def generator():
    pos = 0
    total = len(FULL_TEXT)

    while pos < total:
        size = random.randint(1, 7)
        chunk = FULL_TEXT[pos:pos + size]
        pos += size

        yield serial.to_json({'delta': chunk}) + '\n'

        await asyncio.sleep(random.uniform(0.1, 0.5))
