from loguru import logger
from starlette.authentication import AuthenticationBackend, AuthenticationError, AuthCredentials, BaseUser

from src.core import jwt_token
from src.core.response import Response


class JWTUser(BaseUser):

    def __init__(self, user_id, username, roles):
        self.user_id = user_id
        self.username = username
        self.roles = roles

    @property
    def is_authenticated(self):
        return True

    @property
    def display_name(self):
        return self.username


class JWTAuthBackend(AuthenticationBackend):

    async def authenticate(self, conn):
        auth = conn.headers.get('Authorization')
        if not auth:
            return None
        try:
            scheme, token = auth.split()
            if scheme.lower() != 'bearer':
                return None
            payload = jwt_token.verify_access_token(token)
        except AuthenticationError as e:
            logger.warning(f'[JWT] {e}, path={conn.url.path}')
            raise
        except Exception:
            logger.warning(f'[JWT] Token 解析失败，path={conn.url.path}')
            raise AuthenticationError('JWT Token 解析失败')

        user_id = payload['user_id']
        username = payload['username']
        roles = payload.get('roles', [])

        return AuthCredentials(roles), JWTUser(user_id, username, roles)


def on_auth_error(request, exc):
    return Response(
        {'code': 401, 'msg': str(exc), 'data': None},
        status_code=401,
    )
