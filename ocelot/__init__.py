from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError

from .login.routes import router as login_router
from .login.errors import (
    OcelotError,
    ocelot_exception_handler,
    request_validation_exception_handler,
)

__version__ = "0.1.0"


def create_app() -> FastAPI:
    app = FastAPI()
    app.add_exception_handler(OcelotError, ocelot_exception_handler)
    app.add_exception_handler(
        RequestValidationError, request_validation_exception_handler
    )
    app.include_router(login_router)
    return app


app = create_app()
