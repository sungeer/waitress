import json
from typing import Any

from starlette.responses import JSONResponse

from src.utils.serial import JsonExtendEncoder


class ApiResponse(JSONResponse):

    def render(self, content: Any) -> bytes:
        return json.dumps(
            content,
            cls=JsonExtendEncoder,
            ensure_ascii=False,
            allow_nan=False,
            indent=None,
            separators=(',', ':'),
        ).encode('utf-8')


# 统一响应外壳 {code, msg, data} 仅有的两个对外构造入口：ok / fail


def ok(data=None, msg='success'):
    """成功响应：code 恒为 0
    成功码约定为 0（前端以 code == 0 判成功），直接写死，不引用枚举
    """
    return ApiResponse({'code': 0, 'msg': msg, 'data': data})


def fail(code, msg, data=None, http_status=200, headers=None):
    """失败等其余响应的外壳
    code 业务码语义见 src/core/codes.py
    http_status 默认 200：HTTP 200 + 非零 code 表示业务失败
    """
    return ApiResponse(
        {'code': code, 'msg': msg, 'data': data},
        status_code=http_status,
        headers=headers,
    )
