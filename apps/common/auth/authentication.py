from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import AuthenticationFailed, InvalidToken
from django.utils.translation import gettext_lazy as _
from apps.drivers.models import Driver
from apps.session.models import DriverSession, FactoryUserSession
from data.users.models import FactoryUser

class UnifiedJWTAuthentication(JWTAuthentication):
    def get_user(self, validated_token):
        try:
            user_id = validated_token["user_id"]
            role = validated_token["role"]
            session_id = validated_token["session"]
        except KeyError:
            raise InvalidToken(_("Token contained no recognizable user identification"))

        if role == "driver":
            return self._authenticate_driver(user_id, session_id)
        else:
            return self._authenticate_user(user_id, session_id)

    def _authenticate_user(self, user_id, session_id):
        try:
            user = FactoryUser.objects.get(id=user_id)
        except FactoryUser.DoesNotExist:
            raise AuthenticationFailed(_("User not found"), code="user_not_found")
        
        if not FactoryUserSession.objects.filter(id=session_id, factory_user=user).exists():
            raise AuthenticationFailed(_("Session is invalid or expired"), code="session_invalid")
        
        return user

    def _authenticate_driver(self, user_id, session_id):
        try:
            driver = Driver.objects.get(id=user_id)
        except Driver.DoesNotExist:
            raise AuthenticationFailed(_("Driver not found"), code="user_not_found")
            
        if not DriverSession.objects.filter(id=session_id, driver=driver).exists():
            raise AuthenticationFailed(_("Session is invalid or expired"), code="session_invalid")

        return driver
