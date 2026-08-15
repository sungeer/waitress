from src.core.response import ok
from src.domains.health import service
from src.config import settings


async def startup_probe(request):
    environment = settings.environment
    data = {
        'environment': environment
    }
    return ok(data)


async def liveness(request):
    data = {'status': 'alive'}
    return ok(data)


async def readiness(request):
    await service.check_db_conn()
    data = {'status': 'ready'}
    return ok(data)
