from loguru import logger

from src.utils.exceptions import (
    BusinessError,
    UnauthorizedError,
    ForbiddenError
)
from src.core.response import fail


# 业务失败
async def business_error(request, exc):
    logger.warning(
        'business error method={} path={} code={} msg={}',
        request.method, request.url.path, exc.code, exc.msg,
    )
    # 前端通过 code 判断
    return fail(exc.code, exc.msg, exc.data)


# 未登录
async def unauthorized_error(request, exc):
    # return fail(exc.code, exc.msg, None, http_status=exc.http_status)
    return fail(401, exc.msg, None, http_status=401)


# 无权限 403
async def forbidden_error(request, exc):
    return fail(403, exc.msg, None, http_status=403)


# 路由匹配不到
async def not_found(request, exc):
    return fail(404, exc.detail, None, http_status=404)


# 方法不对
async def method_not_allowed(request, exc):
    return fail(405, exc.detail, None, http_status=405)


# 内部错误 500
async def server_error(request, exc):
    """兜底处理
    数据库崩了 依赖超时 等 系统级异常
    监控在这里感知
    """
    request_id = getattr(request.state, 'request_id', '-')

    with logger.contextualize(request_id=request_id):
        logger.exception('unhandled server error path={}', request.url.path)

    return fail(
        500, 'internal server error',
        None,
        http_status=500,
        headers={'X-Request-ID': request_id}
    )


exception_handlers = {
    404: not_found,  # 整数键 由 Starlette 内部触发
    405: method_not_allowed,  # 整数键 方法不对
    BusinessError: business_error,  # 类键
    UnauthorizedError: unauthorized_error,
    ForbiddenError: forbidden_error,
    Exception: server_error,  # 处理所有没被预料到的 Python 异常
}
