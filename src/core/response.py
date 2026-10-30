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


def ok(data: Any = None) -> ApiResponse:
    return ApiResponse({'success': True, 'data': data})


def fail(
    error: str,
    http_status: int = 200,
    headers: dict | None = None
) -> ApiResponse:
    return ApiResponse(
        {'success': False, 'error': error},
        status_code=http_status,
        headers=headers,
    )
