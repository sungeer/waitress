from loguru import logger
from sqlalchemy.exc import IntegrityError

from src.core.codes import BizCode
from src.core.exceptions import (
    BusinessError,
    UnauthorizedError,
    ForbiddenError
)
from src.core.response import Response


# 业务失败
async def business_error(request, exc):
    logger.warning(
        'business error method={} path={} code={} msg={}',
        request.method, request.url.path, exc.code, exc.msg,
    )
    # 前端通过 code 判断
    return Response.make(exc.code, exc.msg, exc.data)


# 未登录
async def unauthorized_error(request, exc):
    return Response.make(401, exc.msg, None, http_status=401)


# 无权限 403
async def forbidden_error(request, exc):
    return Response.make(403, exc.msg, None, http_status=403)


# 路由匹配不到
async def not_found(request, exc):
    return Response.make(404, exc.detail, None, http_status=404)


# 唯一键/约束冲突兜底
async def integrity_conflict(request, exc):
    logger.warning(
        'integrity conflict method={} path={} code={}',
        request.method, request.url.path, BizCode.RESOURCE_CONFLICT.value,
    )
    return Response.make(
        BizCode.RESOURCE_CONFLICT,
        BizCode.RESOURCE_CONFLICT.message,
        None
    )


# 内部错误 500
async def server_error(request, exc):
    """兜底处理
    数据库崩了 依赖超时 等 系统级异常
    监控在这里感知
    """
    request_id = getattr(request.state, 'request_id', '-')

    with logger.contextualize(request_id=request_id):
        logger.exception('unhandled server error path={}', request.url.path)

    return Response.make(
        500, '服务器内部错误',
        None,
        http_status=500,
        headers={'X-Request-ID': request_id}
    )


exception_handlers = {
    404: not_found,  # 整数键 由 Starlette 内部触发
    500: server_error,  # raise HTTPException(status_code=500, detail='something wrong') 触发
    BusinessError: business_error,  # 类键
    UnauthorizedError: unauthorized_error,
    ForbiddenError: forbidden_error,
    IntegrityError: integrity_conflict,  # 唯一键/约束冲突兜底（预检漏网的竞态等）
    Exception: server_error,  # 必须放最后 处理所有没被预料到的 Python 异常
}
