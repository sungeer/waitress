import asyncio
from datetime import datetime, timedelta

from loguru import logger
from sqlalchemy.exc import IntegrityError

from src.core.db_registry import db
from src.core.executor import executor
from src.core.http_client import httpx, HTTPError
from src.domains.weather import repository
from src.domains.weather.errors import UpstreamError
from src.utils.concurrency import run_in_threadpool

# 快照新鲜度：与 open-meteo 约 15 分钟一更的节奏对齐
SNAPSHOT_TTL_SECONDS = 900

# 连续失败达到该次数 → 对外标记 degraded
DEGRADE_AFTER_FAILURES = 3

# 失败退避：30s * 2^(n-1)，封顶 1 小时
_BACKOFF_BASE_SECONDS = 30
_BACKOFF_CAP_SECONDS = 3600

_FORECAST_URL = 'https://api.open-meteo.com/v1/forecast'


# 每格点一个进程内 asyncio.Lock，保证单飞。字典按"请求过的格点"增长，量级远小于
# 业务量，可接受；若未来多进程部署，需换成 DB 级唯一键 claim(见 core/codes 编号注释的思路)。
_refresh_locks: dict[str, asyncio.Lock] = {}


def now() -> datetime:
    return datetime.now()


def round_coord(value: float, decimals: int = 1) -> float:
    return round(value, decimals)


def cell_of(lat: float, lon: float) -> str:
    return f'{lat:.1f},{lon:.1f}'


def is_expired(fetched_at: datetime, now_time: datetime) -> bool:
    return (now_time - fetched_at).total_seconds() >= SNAPSHOT_TTL_SECONDS


def should_attempt(snap: dict, now_time: datetime) -> bool:
    # 退避冷却期内不发起上游请求，避免对故障源反复冲击
    if snap.get('next_retry_at') is not None and snap.get('consecutive_failures', 0) > 0:
        return now_time >= snap['next_retry_at']
    return True


def to_data(snap: dict, now_time: datetime) -> dict:
    fetched_at = snap['fetched_at']
    fresh = not is_expired(fetched_at, now_time)
    age_s = int((now_time - fetched_at).total_seconds())
    degraded = (not fresh) and snap.get('consecutive_failures', 0) >= DEGRADE_AFTER_FAILURES

    data = dict(snap['payload'])  # 浅拷贝 dict({'a': 'qaz'})
    meta = {
        'cell': snap['cell'],
        'fresh': fresh,
        'age_s': age_s,
        'degraded': degraded,
    }
    data.update(meta)
    return data


def _lock_for(cell: str) -> asyncio.Lock:
    lock = _refresh_locks.get(cell)
    if lock is None:
        lock = asyncio.Lock()
        _refresh_locks[cell] = lock
    return lock


async def _read_snapshot(cell: str) -> dict | None:
    def run_sync():
        with db.connect() as conn:
            return repository.get(conn, cell)

    return await run_in_threadpool(executor.db, run_sync)


async def _store_success(cell: str, payload: dict, has_row: bool):
    def run_sync():
        with db.connect() as conn:
            if has_row:
                repository.update_success(conn, cell, payload, now())
            else:
                try:
                    repository.insert(conn, cell, payload, now())
                except IntegrityError:
                    pass
            conn.commit()

    await run_in_threadpool(executor.db, run_sync)


async def _record_failure(snap: dict, cell: str, error: str):
    failures = snap.get('consecutive_failures', 0) + 1
    delay = min(_BACKOFF_BASE_SECONDS * (2 ** (failures - 1)), _BACKOFF_CAP_SECONDS)
    next_retry_at = now() + timedelta(seconds=delay)
    logger.warning(
        'weather refresh failed cell={} failures={} next_retry_in={}s err={}',
        cell, failures, delay, error
    )

    def run_sync():
        with db.connect() as conn:
            repository.mark_failure(conn, cell, error, next_retry_at)
            conn.commit()

    await run_in_threadpool(executor.db, run_sync)


# 查询天气
async def _fetch_current(cell: str, lat: float, lon: float) -> dict:
    params = {
        'latitude': lat,
        'longitude': lon,
        'current_weather': 'true',
    }
    client = httpx.get()
    resp = await client.get(_FORECAST_URL, params=params)
    resp.raise_for_status()

    payload = resp.json().get('current_weather')
    if not isinstance(payload, dict):
        raise UpstreamError('unexpected open-meteo payload')

    logger.info(
        'weather fetch upstream cell={} lat={} lon={}',
        cell, lat, lon
    )
    return payload


# from db data
async def get_snapshot(cell: str) -> dict | None:
    return await _read_snapshot(cell)


async def refresh_cell(cell: str, lat: float, lon: float) -> dict:
    """单飞刷新
    并发调用同一格点时只有一个真正打上游
    锁内重读避免重复刷新
    拿到锁后若已新鲜或仍在退避冷却则直接返回
    """
    async with _lock_for(cell):
        snap = await _read_snapshot(cell)
        now_time = now()

        if snap and not is_expired(snap['fetched_at'], now_time):
            return snap
        if snap and not should_attempt(snap, now_time):
            return snap

        try:
            payload = await _fetch_current(cell, lat, lon)
        except HTTPError as exc:
            if snap:
                await _record_failure(snap, cell, str(exc))
            raise UpstreamError(f'open-meteo fetch failed: {exc}') from exc

        await _store_success(cell, payload, snap is not None)
        refreshed = await _read_snapshot(cell)
        if refreshed is None:
            raise UpstreamError('snapshot missing right after store')
        return refreshed


async def refresh_runner(cell: str, lat: float, lon: float) -> None:
    """供 background.spawn 调用的静默刷新
    吞掉预期的 UpstreamError，避免后台任务产生未处理异常
    """
    try:
        await refresh_cell(cell, lat, lon)
    except UpstreamError as exc:
        logger.warning(
            'weather background refresh done cell={} err={}',
            cell, exc
        )
