"""应用层 HTTP 异常
用于"请求-响应"流程
"""


class AppError(Exception):
    """所有应用异常的基类"""
    pass


class BusinessError(AppError):
    """业务失败
    HTTP 200 + success=false
    比如 库存不足 用户状态异常 资源不存在
    """
    http_status = 200

    def __init__(self, msg: str):
        self.msg = msg
        super().__init__(self.msg)  # 让 str(exc) 有内容


# 400 入参错误：请求本身不合法，服务端未执行业务逻辑
class ParamError(AppError):
    http_status = 400

    def __init__(self, msg: str):
        self.msg = msg
        super().__init__(msg)


# 503 上游依赖不可用
class UpstreamUnavailableError(AppError):
    http_status = 503

    def __init__(self, msg='upstream data source unavailable'):
        self.msg = msg
        super().__init__(msg)


# 401
class UnauthorizedError(AppError):
    http_status = 401

    def __init__(self, msg='please login first'):
        self.msg = msg
        super().__init__(msg)


# 403
class ForbiddenError(AppError):
    http_status = 403

    def __init__(self, msg='no permission'):
        self.msg = msg
        super().__init__(msg)
