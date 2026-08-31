from typing import Annotated

from pydantic import BaseModel, StringConstraints

NonBlankStr = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1)]


class CreateUserSchema(BaseModel):
    username: NonBlankStr
    display_name: NonBlankStr | None = None
    email: NonBlankStr | None = None
