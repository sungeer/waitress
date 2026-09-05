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


def ok(data=None, msg='success'):
    return ApiResponse({'code': 0, 'msg': msg, 'data': data})


def fail(code, msg, data=None, http_status=200, headers=None):
    return ApiResponse(
        {'code': code, 'msg': msg, 'data': data},
        status_code=http_status,
        headers=headers,
    )
