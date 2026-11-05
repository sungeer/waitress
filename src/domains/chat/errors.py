class UpstreamError(Exception):
    """第三方 API 接口调用失败
    超时  非 2xx  结构异常
    域内控制流专用
    """
    pass


class ReactLoopExhaustedError(Exception):
    """ReAct 循环未在预算内收敛
    属于逻辑异常 不是上游故障
    故意不继承 UpstreamError 避免被映射成 503
    """
    pass
