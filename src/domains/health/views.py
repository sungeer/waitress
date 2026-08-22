from src.config import settings
from src.core.response import ok


async def liveness(request):
    _ = request  # 显式标记为已使用

    data = {
        'environment': settings.environment,
        'status': 'alive'
    }

    return ok(data)
