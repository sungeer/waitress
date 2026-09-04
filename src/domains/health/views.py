from src import settings
from src.core.response import success


async def liveness(request):
    _ = request  # 显式标记为已使用

    data = {
        'environment': settings.ENVIRONMENT,
        'version': settings.VERSION,
    }
    return success(data)
