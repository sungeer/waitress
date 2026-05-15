import functools

from src.core.exceptions import UnauthorizedError, ForbiddenError


# 登录校验
def login_required(func):
    @functools.wraps(func)
    async def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            raise UnauthorizedError()
        return await func(request, *args, **kwargs)

    return wrapper


# 权鉴
def permission_required(scope):
    def decorator(func):
        @functools.wraps(func)
        async def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                raise UnauthorizedError()
            if scope not in request.user.roles:
                raise ForbiddenError(f'需要[{scope}]权限')
            return await func(request, *args, **kwargs)

        return wrapper

    return decorator
