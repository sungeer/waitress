from starlette.responses import StreamingResponse

from src.core.response import ok
from src.domains.chat import service
from src.utils import validate


async def stream(request):  # noqa
    return StreamingResponse(
        service.stream_chunks(),
        media_type='application/x-ndjson',
        headers={
            'Cache-Control': 'no-cache',
            'X-Accel-Buffering': 'no',
        }
    )


async def ask(request):
    body: dict = await validate.require_body(request)
    content = await service.ask()
    return ok(content)


async def structured(request):  # noqa
    content = await service.structured()
    return ok(content)


async def react(request):
    data = await validate.require_body(request)

    question = validate.require_str(data, 'question')
    latitude = validate.require_number(data, 'latitude', -90, 90)
    longitude = validate.require_number(data, 'longitude', -180, 180)

    answer = await service.react(question, latitude, longitude)
    return ok({'answer': answer})
