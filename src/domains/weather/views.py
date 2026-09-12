from src.core.background import background
from src.core.response import ok
from src.domains.weather import service
from src.utils import validate


async def weather_get(request):
    body = await validate.require_body(request)  # dict

    lat = validate.require_float_in(body, 'lat', -90, 90)
    lon = validate.require_float_in(body, 'lon', -180, 180)

    lat_r = service.round_coord(lat)
    lon_r = service.round_coord(lon)
    cell = service.cell_of(lat_r, lon_r)

    now_time = service.now()
    snap = await service.get_or_refresh(cell, lat_r, lon_r)

    data = service.to_data(snap, now_time)

    if not data['fresh'] and service.should_attempt(snap, now_time):
        background.spawn(
            service.refresh_runner(cell, lat_r, lon_r)
        )

    return ok(data)
