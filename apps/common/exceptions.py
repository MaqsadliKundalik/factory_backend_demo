from rest_framework.exceptions import (
    AuthenticationFailed,
    NotFound,
    NotAuthenticated,
    PermissionDenied,
    ValidationError,
)


class WrongPasswordError(NotAuthenticated):
    default_code = "wrong_password"
    default_detail = "Parol noto'g'ri."


class UserNotFoundError(NotFound):
    default_code = "user_not_found"
    default_detail = "Foydalanuvchi topilmadi."


class DriverNotFoundError(NotFound):
    default_code = "driver_not_found"
    default_detail = "Haydovchi topilmadi."


class SessionInvalidError(AuthenticationFailed):
    default_code = "session_invalid"
    default_detail = "Sessiya yaroqsiz yoki muddati tugagan."


class TokenExpiredError(AuthenticationFailed):
    default_code = "token_expired"
    default_detail = "Token muddati tugagan."


class TokenInvalidError(AuthenticationFailed):
    default_code = "token_invalid"
    default_detail = "Token yaroqsiz."


class RefreshTokenRequiredError(AuthenticationFailed):
    default_code = "refresh_token_required"
    default_detail = "Refresh token talab qilinadi."


class RefreshTokenInvalidError(AuthenticationFailed):
    default_code = "refresh_token_invalid"
    default_detail = "Refresh token yaroqsiz yoki muddati tugagan."


class NoPermissionError(PermissionDenied):
    default_code = "no_permission"
    default_detail = "Bu amalni bajarishga ruxsat yo'q."
