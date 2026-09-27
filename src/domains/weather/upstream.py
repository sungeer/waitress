from loguru import logger

from src.core.http_client import httpx, HTTPError, Timeout
from src.domains.weather.errors import UpstreamError

_FORECAST_URL = 'https://api.open-meteo.com/v1/forecast'


# 查询天气
async def fetch_current(cell: str, lat: float, lon: float) -> dict:
    params = {
        'latitude': lat,
        'longitude': lon,
        'current_weather': 'true',
    }
    client = httpx.get()
    timeout = Timeout(connect=3.0, read=15.0, write=5.0, pool=5.0)
    try:
        # await client.get(url, timeout=20)
        resp = await client.get(_FORECAST_URL, params=params, timeout=timeout)
        resp.raise_for_status()
        body = resp.json()
    except (HTTPError, ValueError) as exc:
        raise UpstreamError(f'open-meteo fetch failed: {exc}') from exc

    if not isinstance(body, dict):
        raise UpstreamError('unexpected open-meteo payload shape')

    payload = body.get('current_weather')
    if not isinstance(payload, dict):
        raise UpstreamError('unexpected open-meteo payload')

    logger.info(
        'weather fetch upstream cell={} lat={} lon={}',
        cell, lat, lon
    )
    return payload
