import enum


class ErrorCode(enum.Enum):
    INTERNAL_ERROR = 2
    INVALID_CREDENTIALS = 3


class OcelotError(Exception):
    code: ErrorCode


class InternalError(OcelotError):
    code = ErrorCode.INTERNAL_ERROR


class InvalidCredentials(OcelotError):
    code = ErrorCode.INVALID_CREDENTIALS


error_messages: dict[ErrorCode, str] = {
    ErrorCode.INTERNAL_ERROR: "Internal error. Please try again later or contact customer support if the problem persists.",
    ErrorCode.INVALID_CREDENTIALS: "Tibia account email address or Tibia password is not correct.",
}


def error_response(error_code: ErrorCode):
    return {
        "errorCode": error_code.value,
        "errorMessage": error_messages[error_code],
    }
