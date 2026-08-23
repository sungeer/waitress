import httpx2


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
