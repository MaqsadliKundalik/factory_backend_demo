import jwt
from django.conf import settings
from django.http import JsonResponse
from data.drivers.models import Driver
from data.users.models import FactoryUser
from data.session.models import DriverSession, FactoryUserSession


class CombinedAuthMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def get_token_from_request(self, request):

        # 1. Try Authorization header (e.g., "Bearer <token>")
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            return auth_header.split(" ")[1]

        # 2. Try query parameter (?token=...)
        token = request.GET.get("token")
        if token:
            return token

        return None  # No token found

    def __call__(self, request):
        token = self.get_token_from_request(request)

        # Default to None
        request.driver = None
        request.driver_session = None

        request.operator = None
        request.operator_session = None
        request.manager = None
        request.manager_session = None
        request.guard = None
        request.guard_session = None

        if not token:
            return self.get_response(request)

        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        except IndexError:
            return JsonResponse(
                {"Ошибка": "Неверный формат заголовка Authorization"}, status=401
            )
        except jwt.ExpiredSignatureError:
            return JsonResponse({"Ошибка": "Срок действия токена истёк"}, status=401)
        except jwt.DecodeError:
            return JsonResponse({"Ошибка": "Недействительный токен"}, status=401)

        role = payload.get("role")
        session_id = payload.get("session")
        user_id = payload.get("user_id")

        # Try Driver
        driver_id = payload.get("driver")
        if role == "driver" or driver_id:
            lookup_id = driver_id or user_id
            if lookup_id and session_id:
                try:
                    request.driver = Driver.objects.get(id=lookup_id)
                    request.driver_session = DriverSession.objects.get(id=session_id)
                    return self.get_response(request)
                except (Driver.DoesNotExist, DriverSession.DoesNotExist):
                    pass

        # Try Operator / Manager / Guard
        if role in ("operator", "manager", "guard") and user_id and session_id:
            try:
                user = FactoryUser.objects.get(id=user_id, role=role)
                session = FactoryUserSession.objects.get(id=session_id)
                if role == "operator":
                    request.operator = user
                    request.operator_session = session
                elif role == "manager":
                    request.manager = user
                    request.manager_session = session
                elif role == "guard":
                    request.guard = user
                    request.guard_session = session
                request.role = role
                return self.get_response(request)
            except (FactoryUser.DoesNotExist, FactoryUserSession.DoesNotExist):
                pass

        # Token exists but no role authenticated
        return JsonResponse(
            {"Ошибка": "Неавторизованный доступ: неверная роль или сессия"}, status=401
        )
