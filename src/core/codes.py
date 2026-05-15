from enum import IntEnum


# 业务 状态码
class BizCode(IntEnum):

    def __new__(cls, value: int, message: str = ''):
        obj = int.__new__(cls, value)
        obj._value_ = value
        obj.message = message
        return obj

    # 成功
    OK = (0, '成功')

    # 通用错误
    PARAM_ERROR = (1001, '请求参数错误')
    PARAM_MISSING = (1002, '缺少必要参数')
    PARAM_TYPE_ERROR = (1003, '参数类型错误')
    PARAM_OUT_OF_RANGE = (1004, '参数超出合法范围')
    RESOURCE_NOT_FOUND = (1005, '资源不存在')
    RESOURCE_CONFLICT = (1006, '资源已存在，请勿重复创建')
    OPERATION_NOT_ALLOWED = (1007, '不支持该操作')
    RATE_LIMITED = (1008, '操作过于频繁，请稍后再试')

    # 用户 认证
    USER_NOT_FOUND = (2001, '用户不存在')
    USER_DISABLED = (2002, '账号已被禁用')
    USER_ALREADY_EXISTS = (2003, '用户已存在')
    USER_PASSWORD_WRONG = (2004, '用户名或密码错误')
    USER_NOT_VERIFIED = (2005, '账号尚未完成验证')
    USER_TOKEN_EXPIRED = (2006, 'Token 已过期，请重新登录')
    USER_TOKEN_INVALID = (2007, 'Token 无效')
    USER_PHONE_BOUND = (2008, '该手机号已绑定其他账号')

    # 商品 库存
    ITEM_NOT_FOUND = (3001, '商品不存在')
    ITEM_OFF_SHELF = (3002, '商品已下架')
    ITEM_NOT_AVAILABLE = (3003, '商品暂不可购买')
    STOCK_INSUFFICIENT = (3004, '库存不足')
    STOCK_LOCKED = (3005, '库存锁定中，请稍后重试')

    # 订单
    ORDER_NOT_FOUND = (4001, '订单不存在')
    ORDER_EXPIRED = (4002, '订单已超时，请重新下单')
    ORDER_ALREADY_PAID = (4003, '订单已支付')
    ORDER_CANCELLED = (4004, '订单已取消')
    ORDER_STATUS_INVALID = (4005, '订单状态异常，无法执行此操作')
    ORDER_QUANTITY_LIMIT = (4006, '超出单次购买数量限制')

    # 支付 退款
    PAYMENT_FAILED = (5001, '支付失败，请重试')
    PAYMENT_TIMEOUT = (5002, '支付超时，请重新发起')
    PAYMENT_ALREADY_DONE = (5003, '该订单已完成支付，请勿重复操作')
    REFUND_FAILED = (5004, '退款申请失败')
    REFUND_NOT_ALLOWED = (5005, '该订单不满足退款条件')


if __name__ == '__main__':
    print(BizCode.OK)
    print(BizCode.OK.message)
    print(BizCode.PARAM_ERROR)
