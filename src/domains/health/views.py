from src import settings
from src.core.response import ok


async def liveness(request):
    _ = request  # 显式标记为已使用

    data = {
        'environment': settings.ENVIRONMENT,
        'version': settings.VERSION,
    }
    return ok(data)
