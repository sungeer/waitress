from starlette.responses import StreamingResponse

from src.core.response import ok
from src.domains.chat import service


async def stream(request):  # noqa
    return StreamingResponse(
        service.stream_chunks(),
        media_type='application/x-ndjson',
        headers={
            'Cache-Control': 'no-cache',
            'X-Accel-Buffering': 'no',
        }
    )


async def ask(request):  # noqa
    content = await service.ask()
    return ok(content)


async def structured(request):  # noqa
    content = await service.structured()
    return ok(content)
