from enum import IntEnum


# 业务 状态码
class BizCode(IntEnum):

    def __new__(cls, value: int, message: str = ''):
        obj = int.__new__(cls, value)
        obj._value_ = value
        obj.message = message
        return obj

    # 通用 参数错误
    PARAM_ERROR = (1001, 'invalid request parameters')
    PARAM_MISSING = (1002, 'missing required parameter')
    PARAM_TYPE_ERROR = (1003, 'parameter type error')
    PARAM_OUT_OF_RANGE = (1004, 'parameter out of allowed range')

    # 资源 冲突（唯一键/约束冲突兜底）
    RESOURCE_CONFLICT = (1006, 'resource already exists')

    # 外部依赖
    UPSTREAM_UNAVAILABLE = (1009, 'upstream data source unavailable')

    # 用户
    USER_NOT_FOUND = (2001, 'user not found')
    USER_ALREADY_EXISTS = (2003, 'user already exists')
