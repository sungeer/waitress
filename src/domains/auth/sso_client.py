import httpx

from src.core.config import settings


class SSOError(Exception):
    """SSO 认证失败"""

    def __init__(self, msg='SSO 认证失败'):
        self.msg = msg


class SSOClient:
    """公司 SSO 客户端

    约定 SSO 接口：
      POST {base_url}{verify_path}
      body: { username, password }
      成功: { code: 0, data: { staff_id, username, display_name, email, department } }
      失败: { code: 非0, msg: '...' }
    """

    def __init__(self):
        self.base_url = settings.sso_base_url
        self.verify_path = settings.sso_verify_path

    async def verify(self, username: str, password: str) -> dict:
        async with httpx.AsyncClient(timeout=settings.sso_timeout) as client:
            resp = await client.post(
                f'{self.base_url}{self.verify_path}',
                json={'username': username, 'password': password},
            )
            resp.raise_for_status()
            data = resp.json()

        if data.get('code') != 0:
            raise SSOError(data.get('msg', 'SSO 认证失败'))

        return data['data']


sso_client = SSOClient()
