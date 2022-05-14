import enum
from starlette.responses import JSONResponse


class ErrorCode(enum.Enum):
    INTERNAL_ERROR = 2
    INVALID_CREDENTIALS = 3


error_messages = {
    ErrorCode.INTERNAL_ERROR: "Internal error. Please try again later or contact customer support if the problem persists.",
    ErrorCode.INVALID_CREDENTIALS: "Tibia account email address or Tibia password is not correct.",
}


def error_response(code: ErrorCode):
    return JSONResponse({"errorCode": code.value, "errorMessage": error_messages[code]})




