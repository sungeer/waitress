from loguru import logger

from src.core.background import background
from src.core.codes import BizCode
from src.core.exceptions import BusinessError
from src.core.response import ok
from src.domains.weather import service
from src.domains.weather.errors import UpstreamError
from src.utils import validate


async def _refresh_runner(cell, lat, lon):
    # 后台刷新失败已在 service 记录并退避，这里吞掉以免后台任务异常告警
    try:
        await service.refresh_cell(cell, lat, lon)
    except UpstreamError as exc:
        logger.warning('weather background refresh done cell={} err={}', cell, exc)


async def weather_get(request):
    data = await validate.require_body(request)  # dict

    lat = validate.require_float_in(data, 'lat', -90, 90)
    lon = validate.require_float_in(data, 'lon', -180, 180)

    lat_r = service.round_coord(lat)
    lon_r = service.round_coord(lon)
    cell = service.cell_of(lat_r, lon_r)

    snap = await service.get_snapshot(cell)
    now_time = service.now()

    if snap is None:
        # 冷查：本格从无缓存，只能同步拉一次；上游不可达 → 显式业务失败
        try:
            snap = await service.refresh_cell(cell, lat_r, lon_r)
        except UpstreamError:
            raise BusinessError(BizCode.UPSTREAM_UNAVAILABLE)
        return ok(service.to_data(snap, now_time))

    data = service.to_data(snap, now_time)

    if not data['fresh'] and service.should_attempt(snap, now_time):
        background.spawn(_refresh_runner(cell, lat_r, lon_r))

    return ok(data)
