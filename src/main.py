from starlette.applications import Starlette

from src.core.lifespan import lifespan
from src.core.handlers import exception_handlers
from src.middleware import middleware
from src.routes import routes


def create_app():
    app = Starlette(
        routes=routes,
        middleware=middleware,
        exception_handlers=exception_handlers,
        lifespan=lifespan
    )
    return app
