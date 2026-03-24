from rest_framework.views import exception_handler
from rest_framework.exceptions import ValidationError


def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)

    if response is not None:
        code = getattr(exc, "default_code", None) or "error"

        if isinstance(exc, ValidationError):
            response.data = {
                "code": "validation_error",
                "detail": response.data,
            }
        else:
            response.data = {
                "code": code,
                "detail": response.data.get("detail", str(exc)),
            }

    return response
