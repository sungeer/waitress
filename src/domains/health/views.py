from src import settings
from src.core.response import ok


async def liveness(request):
    data = {
        'environment': settings.ENVIRONMENT,
        'version': settings.VERSION,
    }
    return ok(data)
