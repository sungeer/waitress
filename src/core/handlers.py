from loguru import logger

from src.core.exceptions import BusinessError, BadRequestError, UnauthorizedError, ForbiddenError
from src.core.response import Response


# 业务失败
async def business_error(request, exc):
    # 前端通过 code 判断
    return Response(
        {'code': exc.code, 'msg': exc.msg, 'data': exc.data},
        status_code=200,
    )


# 请求参数错误
async def bad_request(request, exc):
    return Response(
        {'code': 400, 'msg': exc.msg, 'data': None},
        status_code=400,
    )


# 未登录
async def unauthorized_error(request, exc):
    return Response(
        {'code': 401, 'msg': exc.msg, 'data': None},
        status_code=401,
    )


# 无权限 403
async def forbidden_error(request, exc):
    return Response(
        {'code': 403, 'msg': exc.msg, 'data': None},
        status_code=403,
    )


# 路由匹配不到
async def not_found(request, exc):
    return Response(
        {'code': 404, 'msg': exc.detail, 'data': None},
        status_code=404,
    )


# 内部错误 500
async def server_error(request, exc):
    """兜底处理
    数据库崩了 依赖超时 等 系统级异常
    监控在这里感知
    """
    logger.exception(f'{request.url.path}')
    return Response(
        {'code': 500, 'msg': '服务器内部错误', 'data': None},
        status_code=500,
    )


exception_handlers = {
    404: not_found,  # 整数键 由 Starlette 内部触发
    500: server_error,  # raise HTTPException(status_code=500, detail='something wrong') 触发
    BusinessError: business_error,  # 类键
    BadRequestError: bad_request,
    UnauthorizedError: unauthorized_error,
    ForbiddenError: forbidden_error,
    Exception: server_error,  # 必须放最后 处理所有没被预料到的 Python 异常
}
