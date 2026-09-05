class UpstreamError(Exception):
    """open-meteo 拉取失败
    超时  非 2xx  结构异常
    域内控制流专用
    """
    pass
