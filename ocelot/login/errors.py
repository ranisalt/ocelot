import enum

from fastapi import Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse


class ErrorCode(enum.Enum):
    INTERNAL_ERROR = 2
    INVALID_CREDENTIALS = 3


error_messages = {
    ErrorCode.INTERNAL_ERROR: "Internal error. Please try again later or contact customer support if the problem persists.",
    ErrorCode.INVALID_CREDENTIALS: "Tibia account email address or Tibia password is not correct.",
}


class OcelotError(Exception):
    def __init__(self, code: ErrorCode, message: str):
        super().__init__()
        self.code = code
        self.message = message


def error_response(code: ErrorCode) -> OcelotError:
    return OcelotError(code=code, message=error_messages[code])


def request_validation_exception_handler(request: Request, exc: RequestValidationError):
    return ocelot_exception_handler(
        request, error_response(ErrorCode.INVALID_CREDENTIALS)
    )


def ocelot_exception_handler(request: Request, exc: OcelotError):
    return JSONResponse(
        content={"errorCode": exc.code.value, "errorMessage": exc.message}
    )
