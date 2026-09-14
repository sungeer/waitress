from contextlib import suppress

import httpx2

# 统一暴露传输层错误，供上层捕获，避免各域直接依赖具体 HTTP 包
HTTPError = httpx2.HTTPError

# 供调用方按请求覆盖超时，不必直接依赖 httpx2
Timeout = httpx2.Timeout


class _AsyncClientHolder:

    def __init__(self):
        self._client = None

    def init(self):
        # 默认 100 条连接
        # self._client = httpx2.AsyncClient(timeout=5.0, verify=False)
        self._client = httpx2.AsyncClient(
            timeout=httpx2.Timeout(
                connect=5.0,  # 连接阶段快速失败
                read=90.0,  # 给服务端留足处理时间
                write=10.0,  # 发送请求体
                pool=30.0  # 池排队超时
            ),
            limits=httpx2.Limits(
                max_connections=800,  # 同一时刻允许建立的总连接数上限,包括正在使用中的 + 空闲的
                # max_keepalive_connections=200,  # 连接池里允许保留的空闲连接数上限,约为 max 的 25%
                keepalive_expiry=0.0,  # 复用有效期,小于服务端的超时时间
            ),
            verify=False,
        )

    def get(self):
        if self._client is None:
            raise RuntimeError('HTTP client not initialized')
        return self._client

    async def aclose(self):
        if self._client is not None:
            with suppress(Exception):
                await self._client.aclose()
            self._client = None


httpx = _AsyncClientHolder()
