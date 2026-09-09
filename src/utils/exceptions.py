class AppError(Exception):
    """所有应用异常的基类"""
    pass


class BusinessError(AppError):
    """业务失败
    HTTP 200 + 非零 business code
    比如 库存不足 用户状态异常 参数业务校验失败
    """

    def __init__(self, code: int, msg: str | None = None, data=None):
        self.code = code
        # 只传 code（如 BizCode 枚举）时自动取自带文案，避免 code/msg 成对重复
        self.msg = msg if msg is not None else getattr(code, 'message', '')
        self.data = data


# 401
class UnauthorizedError(AppError):

    def __init__(self, msg='请先登录'):
        self.msg = msg


# 403
class ForbiddenError(AppError):

    def __init__(self, msg='无权限'):
        self.msg = msg
