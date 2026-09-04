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
def success(data=None, msg='success'):
    # 成功码约定为 0（前端以 code == 0 判成功），直接写死，不引用枚举
    return Response.make(0, msg, data)
