import json
from typing import Any

from starlette.responses import JSONResponse

from src.utils.serial import JsonExtendEncoder


class Response(JSONResponse):

    def render(self, content: Any) -> bytes:
        return json.dumps(
            content,
            cls=JsonExtendEncoder,
            ensure_ascii=False,
            allow_nan=False,
            indent=None,
            separators=(',', ':'),
        ).encode('utf-8')


# 成功响应
def ok(data=None, msg='success'):
    return Response({
        'code': 0,
        'msg': msg,
        'data': data,
    })


# 业务失败响应
def fail(code: int, msg: str, data=None):
    """业务失败响应
    HTTP 状态码仍为 200
    通常不直接调用，而是通过 raise BusinessError 触发
    """
    return Response({
        'code': code,
        'msg': msg,
        'data': data,
    }, status_code=200)
