from src.core.response import ok, Response
from src.domains.health import service
from src.core.startup_state import startup_state


async def startup_probe(request):
    not_ready = []
    if not startup_state.app_started:
        not_ready.append('app_started')
    if not_ready:
        # 主动返回 503 禁止走异常链路
        return Response(
            {'code': 503, 'msg': 'starting', 'data': {'pending': not_ready}},
            status_code=503,
        )
    data = {'status': 'started'}
    return ok(data)


async def liveness(request):
    data = {'status': 'alive'}
    return ok(data)


async def readiness(request):
    await service.check_db_conn()
    data = {'status': 'ready'}
    return ok(data)
