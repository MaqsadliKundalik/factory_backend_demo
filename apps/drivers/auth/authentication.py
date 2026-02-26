from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import AuthenticationFailed, InvalidToken
from django.utils.translation import gettext_lazy as _
from apps.drivers.models import Driver
from apps.session.models import DriverSession

class DriverJWTAuthentication(JWTAuthentication):

    def get_user(self, validated_token):
        """
        Returns the user model instance associated with the token, if one exists.
        This overrides the default behavior to return a Driver instance.
        """
        try:
            user_id = validated_token["user_id"]
            role = validated_token["role"]
            session_id = validated_token["session"]
        except KeyError:
            raise InvalidToken(_("Token contained no recognizable user identification"))

        if role != "driver":
             raise AuthenticationFailed(_("Token is not for a driver"), code="role_invalid")

        try:
            driver = Driver.objects.get(id=user_id)
        except Driver.DoesNotExist:
            raise AuthenticationFailed(_("Driver not found"), code="driver_not_found")
            
        try:
            # Check if session is still valid
            DriverSession.objects.get(id=session_id, driver=driver)
        except DriverSession.DoesNotExist:
            raise AuthenticationFailed(_("Session is invalid or expired"), code="session_invalid")

        return driver
