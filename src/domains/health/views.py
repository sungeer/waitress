from src import settings
from src.core.response import success


async def liveness(request):
    data = {
        'environment': settings.ENVIRONMENT,
        'version': settings.VERSION,
    }
    return success(data)
