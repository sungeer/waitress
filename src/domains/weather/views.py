from src.core.background import background
from src.core.codes import BizCode
from src.core.exceptions import BusinessError
from src.core.response import ok
from src.domains.weather import service
from src.domains.weather.errors import UpstreamError
from src.utils import validate


async def weather_get(request):
    data = await validate.require_body(request)  # dict

    lat = validate.require_float_in(data, 'lat', -90, 90)
    lon = validate.require_float_in(data, 'lon', -180, 180)

    lat_r = service.round_coord(lat)
    lon_r = service.round_coord(lon)
    cell = service.cell_of(lat_r, lon_r)

    snap = await service.get_snapshot(cell)  # db data
    now_time = service.now()

    if snap is None:
        try:
            snap = await service.refresh_cell(cell, lat_r, lon_r)
        except UpstreamError:
            raise BusinessError(BizCode.UPSTREAM_UNAVAILABLE)
        return ok(service.to_data(snap, now_time))

    data = service.to_data(snap, now_time)

    if not data['fresh'] and service.should_attempt(snap, now_time):
        background.spawn(
            service.refresh_runner(cell, lat_r, lon_r)
        )

    return ok(data)
