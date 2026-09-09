from enum import IntEnum


# 业务 状态码
class BizCode(IntEnum):

    def __new__(cls, value: int, message: str = ''):
        obj = int.__new__(cls, value)
        obj._value_ = value
        obj.message = message
        return obj

    # 通用 参数错误
    PARAM_ERROR = (1001, '请求参数错误')
    PARAM_MISSING = (1002, '缺少必要参数')
    PARAM_TYPE_ERROR = (1003, '参数类型错误')
    PARAM_OUT_OF_RANGE = (1004, '参数超出合法范围')

    # 资源 冲突（唯一键/约束冲突兜底）
    RESOURCE_CONFLICT = (1006, '资源已存在，请勿重复创建')

    # 外部依赖
    UPSTREAM_UNAVAILABLE = (1009, '上游数据源暂不可用')

    # 用户
    USER_NOT_FOUND = (2001, '用户不存在')
    USER_ALREADY_EXISTS = (2003, '用户已存在')
