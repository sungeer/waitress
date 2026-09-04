class AppError(Exception):
    """所有应用异常的基类"""
    pass


class BusinessError(AppError):
    """业务失败
    HTTP 200 + 非零 business code
    比如 库存不足 用户状态异常 参数业务校验失败
    """

    def __init__(self, code: int, msg: str, data=None):
        self.code = code
        self.msg = msg
        self.data = data


# 400
class BadRequestError(AppError):

    def __init__(self, msg='请求参数错误'):
        self.msg = msg


# 401
class UnauthorizedError(AppError):

    def __init__(self, msg='请先登录'):
        self.msg = msg


# 403
class ForbiddenError(AppError):

    def __init__(self, msg='无权限'):
        self.msg = msg
