import enum


class ErrorCode(enum.Enum):
    INVALID_CREDENTIALS = 3


error_messages: dict[ErrorCode, str] = {
    ErrorCode.INVALID_CREDENTIALS: "Tibia account email address or Tibia password is not correct.",
}


def error_response(error_code: ErrorCode):
    return {
        "errorCode": error_code.value,
        "errorMessage": error_messages[error_code],
    }
