import httpx2


# 统一暴露传输层错误，供上层捕获，避免各域直接依赖具体 HTTP 包
HTTPError = httpx2.HTTPError


class _AsyncClientHolder:

    def __init__(self):
        self._client = None

    def init(self):
        # 默认 100 条连接
        self._client = httpx2.AsyncClient(timeout=5.0, verify=False)

    def get(self):
        if self._client is None:
            raise RuntimeError('HTTP client not initialized')
        return self._client

    async def aclose(self):
        if self._client is not None:
            await self._client.aclose()
            self._client = None


httpx = _AsyncClientHolder()
