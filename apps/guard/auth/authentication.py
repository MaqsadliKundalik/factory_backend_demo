from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import AuthenticationFailed, InvalidToken
from django.utils.translation import gettext_lazy as _
from apps.guard.models import Guard
from apps.session.models import GuardSession

class GuardJWTAuthentication(JWTAuthentication):

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

        if role != "guard":
             raise AuthenticationFailed(_("Token is not for a guard"), code="role_invalid")

        try:
            guard = Guard.objects.get(id=user_id)
        except Guard.DoesNotExist:
            raise AuthenticationFailed(_("Guard not found"), code="guard_not_found")
            
        try:
            # Check if session is still valid
            GuardSession.objects.get(id=session_id, guard=guard)
        except GuardSession.DoesNotExist:
            raise AuthenticationFailed(_("Session is invalid or expired"), code="session_invalid")

        return guard
