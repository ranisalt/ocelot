import enum

from starlette.responses import JSONResponse


class ErrorCode(enum.Enum):
    INTERNAL_ERROR = 2
    INVALID_CREDENTIALS = 3
    CHECK_PASSWORD_EMPTY_PASSWORD = 11
    ACCOUNT_CREATION_EMPTY_EMAIL = 57
    ACCOUNT_CREATION_INVALID_EMAIL = 59
    ACCOUNT_CREATION_PASSWORD_DOES_NOT_MEET_REQUIREMENTS = 87
    ACCOUNT_CREATION_INTERNAL_ERROR = 101


error_messages = {
    ErrorCode.INTERNAL_ERROR: "Internal error. Please try again later or contact customer support if the problem persists.",
    ErrorCode.INVALID_CREDENTIALS: "Tibia account email address or Tibia password is not correct.",
    ErrorCode.CHECK_PASSWORD_EMPTY_PASSWORD: "Please enter a password.",
    ErrorCode.ACCOUNT_CREATION_EMPTY_EMAIL: "Please enter your email address!",
    ErrorCode.ACCOUNT_CREATION_INVALID_EMAIL: "This email address has an invalid format. Please enter a correct email address!",
    ErrorCode.ACCOUNT_CREATION_INTERNAL_ERROR: "An internal error has occurred. Please try again later!",
    ErrorCode.ACCOUNT_CREATION_PASSWORD_DOES_NOT_MEET_REQUIREMENTS: "Your password does not meet the requirements",
}


def error_response(code: ErrorCode, **kwargs):
    return JSONResponse(
        {"errorCode": code.value, "errorMessage": error_messages[code], **kwargs}
    )
