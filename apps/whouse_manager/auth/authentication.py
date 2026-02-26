from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import AuthenticationFailed, InvalidToken
from django.utils.translation import gettext_lazy as _
from apps.whouse_manager.models import WhouseManager
from apps.session.models import WhouseManagerSession

class WhouseManagerJWTAuthentication(JWTAuthentication):
    def get_user(self, validated_token):
        try:
            manager_id = validated_token["whouse_manager"]
            session_id = validated_token["session"]
        except KeyError:
            raise InvalidToken(_("Token contained no recognizable user identification"))

        try:
            manager = WhouseManager.objects.get(id=manager_id)
        except WhouseManager.DoesNotExist:
            raise AuthenticationFailed(_("Whouse Manager not found"), code="manager_not_found")
            
        try:
            WhouseManagerSession.objects.get(id=session_id, whouse_manager=manager)
        except WhouseManagerSession.DoesNotExist:
            raise AuthenticationFailed(_("Session is invalid or expired"), code="session_invalid")

        return manager
