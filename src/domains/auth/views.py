from pydantic import ValidationError

from src.core.response import ok
from src.core.exceptions import BadRequestError
from src.domains.auth import service
from src.domains.auth.schema import LoginInSchema


async def login(request):
    data = await request.json()
    try:
        data = LoginInSchema.model_validate(data)
    except ValidationError:
        raise BadRequestError()

    result = await service.login(data.username, data.password)
    return ok(result)
