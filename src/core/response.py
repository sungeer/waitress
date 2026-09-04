import json
from typing import Any

from starlette.responses import JSONResponse

from src.core.codes import BizCode
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

    @classmethod
    def make(cls, code: int, msg: str, data=None, http_status: int = 200, headers=None):
        """统一响应外壳 {code, msg, data} 的唯一构造入口
        code 业务码语义见 src/core/codes.py
        """
        return cls(
            {'code': code, 'msg': msg, 'data': data},
            status_code=http_status,
            headers=headers,
        )


# 成功响应
def ok(data=None, msg='success'):
    return Response.make(BizCode.OK, msg, data)


# 业务失败响应
def fail(code: int, msg: str, data=None):
    """业务失败响应
    HTTP 状态码仍为 200
    通常不直接调用，而是通过 raise BusinessError 触发
    """
    return Response.make(code, msg, data)
