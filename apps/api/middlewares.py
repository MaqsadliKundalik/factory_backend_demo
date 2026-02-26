import jwt
from django.conf import settings
from django.http import JsonResponse
from apps.drivers.models import Driver
from apps.session.models import DriverSession


class CombinedAuthMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def get_token_from_request(self, request):

        # 1. Try Authorization header (e.g., "Bearer <token>")
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            return auth_header.split(" ")[1]

        # 2. Try query parameter (?token=.x`x````````wrererrrerrerrreee`..)
        token = request.GET.get("token")
        if token:
            return token

        return None  # No token found

    def __call__(self, request):
        # auth_header = request.headers.get("Authorization")
        token = self.get_token_from_request(request)

        # Default to None
        request.driver = None
        request.driver_session = None

        request.role = None


        if not token:
            return self.get_response(request)

        try:
            # token = auth_header.split(" ")[1]
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        except IndexError:
            return JsonResponse(
                {"error": "Invalid Authorization header format"}, status=401
            )
        except jwt.ExpiredSignatureError:
            return JsonResponse({"error": "Token has expired"}, status=401)
        except jwt.DecodeError:
            return JsonResponse({"error": "Invalid token"}, status=401)

        # Try Driver
        driver_id = payload.get("driver")
        driver_session_id = payload.get("session")
        if driver_id and driver_session_id:
            try:
                request.driver = Driver.objects.get(id=driver_id)
                request.driver_session = DriverSession.objects.get(
                    id=driver_session_id
                )
                request.role = "DRIVER"
                return self.get_response(request)
            except (Driver.DoesNotExist, DriverSession.DoesNotExist):
                pass

        # Token exists but neither role authenticated
        return JsonResponse(
            {"error": "Unauthorized access: role or session invalid"}, status=401
        )
