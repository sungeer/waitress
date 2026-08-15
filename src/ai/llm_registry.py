import httpx
from langchain_openai import ChatOpenAI

from src.config import settings


class _LLMRegistry:

    def __init__(self):
        self._client = None
        self._store = {}

    def init(self):
        self._client = httpx.Client(verify=False)  # 内网代理 禁用 SSL

        self._store = {
            'common': ChatOpenAI(
                model=settings.llm_common_model,
                base_url=settings.llm_common_url,
                api_key=settings.llm_common_key,  # noqa
                extra_body={'thinking': {'type': 'disabled'}},
                temperature=0.0,
                timeout=120,
                streaming=False,
                http_client=self._client,
            ),
            'streaming': ChatOpenAI(
                model=settings.llm_common_model,
                base_url=settings.llm_common_url,
                api_key=settings.llm_common_key,  # noqa
                extra_body={'thinking': {'type': 'disabled'}},
                temperature=0.0,
                timeout=120,
                streaming=True,
                http_client=self._client,
            ),
            'thinking': ChatOpenAI(
                model=settings.llm_common_model,
                base_url=settings.llm_common_url,
                api_key=settings.llm_common_key,  # noqa
                extra_body={'thinking': {'type': 'enabled'}},
                temperature=0.0,
                timeout=120,
                streaming=True,
                http_client=self._client,
            ),
        }

    def close(self):
        if self._client:
            self._client.close()
            self._client = None
        self._store.clear()

    def get(self, name):
        if not self._store:
            raise RuntimeError('LLMRegistry has not been initialized')
        if name not in self._store:
            raise KeyError(f'llm [{name}] not registered, available: {list(self._store.keys())}')
        return self._store[name]

    # registry['common']
    def __getitem__(self, name):
        return self.get(name)


llm_registry = _LLMRegistry()
