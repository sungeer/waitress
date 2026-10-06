from src import settings
from src.core.response import ok


async def liveness(request):
    data = {
        'env': settings.ENVIRONMENT,
        'version': settings.VERSION,
    }
    return ok(data)
