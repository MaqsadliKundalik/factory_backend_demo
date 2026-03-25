from rest_framework.exceptions import (
    AuthenticationFailed,
    NotFound,
    NotAuthenticated,
    PermissionDenied,
    ValidationError,
)


# ─── Authentication ───────────────────────────────────────────────────────────

class WrongPasswordError(NotAuthenticated):
    default_code = "wrong_password"
    default_detail = "Parol noto'g'ri."


class WrongOldPasswordError(ValidationError):
    default_code = "wrong_old_password"
    default_detail = "Eski parol noto'g'ri."


class SessionInvalidError(AuthenticationFailed):
    default_code = "session_invalid"
    default_detail = "Sessiya yaroqsiz yoki muddati tugagan."


class SessionNotFoundError(NotFound):
    default_code = "session_not_found"
    default_detail = "Sessiya topilmadi."


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


class RoleInvalidError(AuthenticationFailed):
    default_code = "role_invalid"
    default_detail = "Token roli mos kelmaydi."


# ─── Permission ───────────────────────────────────────────────────────────────

class NoPermissionError(PermissionDenied):
    default_code = "no_permission"
    default_detail = "Bu amalni bajarishga ruxsat yo'q."


# ─── User / Driver ────────────────────────────────────────────────────────────

class UserNotFoundError(NotFound):
    default_code = "user_not_found"
    default_detail = "Foydalanuvchi topilmadi."


class DriverNotFoundError(NotFound):
    default_code = "driver_not_found"
    default_detail = "Haydovchi topilmadi."


class PhoneNumberAlreadyExistsError(ValidationError):
    default_code = "phone_number_already_exists"
    default_detail = "Bu telefon raqami allaqachon ro'yxatdan o'tgan."


# ─── Client / Supplier ────────────────────────────────────────────────────────

class ClientNotFoundError(NotFound):
    default_code = "client_not_found"
    default_detail = "Mijoz topilmadi."


class SupplierNotFoundError(NotFound):
    default_code = "supplier_not_found"
    default_detail = "Ta'minotchi topilmadi."


# ─── Product ──────────────────────────────────────────────────────────────────

class ProductNotFoundError(NotFound):
    default_code = "product_not_found"
    default_detail = "Mahsulot topilmadi."


# ─── Order ────────────────────────────────────────────────────────────────────

class OrderNotFoundError(NotFound):
    default_code = "order_not_found"
    default_detail = "Buyurtma topilmadi."


# ─── Transport / Excavator ───────────────────────────────────────────────────

class TransportNotFoundError(NotFound):
    default_code = "transport_not_found"
    default_detail = "Transport topilmadi."


class ExcavatorNotFoundError(NotFound):
    default_code = "excavator_not_found"
    default_detail = "Ekskavator topilmadi."


# ─── Warehouse ────────────────────────────────────────────────────────────────

class WarehouseNotFoundError(NotFound):
    default_code = "warehouse_not_found"
    default_detail = "Ombor topilmadi."
