"""应用层 HTTP 异常
用于"请求-响应"流程
"""


class AppError(Exception):
    """所有应用异常的基类"""
    pass


class BusinessError(AppError):
    """业务失败
    HTTP 200 + 非零 business code
    比如 库存不足 用户状态异常 参数业务校验失败
    """
    http_status = 200

    def __init__(self, code: int, msg: str | None = None, data=None):
        self.code = code
        # 只传 code（如 BizCode 枚举）时自动取自带文案，避免 code/msg 成对重复
        self.msg = msg if msg is not None else getattr(code, 'message', '')
        self.data = data
        super().__init__(self.msg)  # 让 str(exc) 有内容


# 401
class UnauthorizedError(AppError):
    code = 401
    http_status = 401

    def __init__(self, msg='please login first'):
        self.msg = msg
        super().__init__(msg)


# 403
class ForbiddenError(AppError):
    code = 403
    http_status = 403

    def __init__(self, msg='no permission'):
        self.msg = msg
        super().__init__(msg)
