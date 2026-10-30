from loguru import logger
from starlette.requests import ClientDisconnect

from src.utils.exceptions import (
    BusinessError,
    ParamError,
    UpstreamUnavailableError,
    UnauthorizedError,
    ForbiddenError
)
from src.core.response import fail


# 业务失败
async def business_error(request, exc):
    logger.warning(
        'business error, method={}, path={}, msg={}',
        request.method, request.url.path, exc.msg,
    )
    # 前端通过 HTTP 状态 + success 判断
    # 业务拒绝是唯一允许 200 的失败场景
    return fail(exc.msg, http_status=200)


# 入参错误 400
async def param_error(request, exc):
    logger.warning(
        'param error, method={}, path={}, msg={}',
        request.method, request.url.path, exc.msg,
    )
    return fail(exc.msg, http_status=400)


# 上游依赖不可用 503
async def upstream_unavailable(request, exc):
    request_id = getattr(request.state, 'request_id', '-')

    with logger.contextualize(request_id=request_id):
        logger.exception('upstream unavailable, path={}', request.url.path)

    return fail(
        exc.msg,
        http_status=503,
        headers={'X-Request-ID': request_id}
    )


# 未登录
async def unauthorized_error(request, exc):
    return fail(exc.msg, http_status=401)


# 无权限 403
async def forbidden_error(request, exc):
    return fail(exc.msg, http_status=403)


# 路由匹配不到
async def not_found(request, exc):
    return fail(exc.detail, http_status=404)


# 方法不对
async def method_not_allowed(request, exc):
    return fail(exc.detail, http_status=405)


# 客户端中途断开
async def client_disconnect(request, exc):
    return fail('client closed request', http_status=499)


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
        'internal server error',
        http_status=500,
        headers={'X-Request-ID': request_id}
    )


exception_handlers = {
    404: not_found,  # 整数键 由 Starlette 内部触发
    405: method_not_allowed,  # 整数键 方法不对
    BusinessError: business_error,  # 类键
    ParamError: param_error,
    UpstreamUnavailableError: upstream_unavailable,
    UnauthorizedError: unauthorized_error,
    ForbiddenError: forbidden_error,
    ClientDisconnect: client_disconnect,
    Exception: server_error,  # 处理所有没被预料到的 Python 异常
}
