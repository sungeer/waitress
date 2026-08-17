import asyncio
from unittest.mock import patch

from src.domains.tasks import service


async def fast_sleep(*args, **kwargs):
    return None


async def main():
    # 正常路径：任务正常执行，不抛异常
    with patch('asyncio.sleep', new=fast_sleep):
        await service.blocking_caller('ok')
    print('正常路径通过')

    # 异常路径：内部抛异常时，被 logger.exception 记录且被吞掉（await 不向外抛）
    with patch('asyncio.sleep', side_effect=RuntimeError('boom')):
        with patch('src.domains.tasks.service.logger.exception') as mock_exc:
            await service.blocking_caller('bad')

    mock_exc.assert_called_once()
    print('异常路径通过：logger.exception 被调用，异常未向外抛出')

    print('t_tasks_service: all assertions passed')


if __name__ == '__main__':
    asyncio.run(main())
