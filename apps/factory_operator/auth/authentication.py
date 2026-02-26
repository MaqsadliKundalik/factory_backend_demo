from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import AuthenticationFailed, InvalidToken
from django.utils.translation import gettext_lazy as _
from apps.factory_operator.models import FactoryOperator
from apps.session.models import FactoryOperatorSession

class FactoryOperatorJWTAuthentication(JWTAuthentication):
    def get_user(self, validated_token):
        try:
            operator_id = validated_token["factory_operator"]
            session_id = validated_token["session"]
        except KeyError:
            raise InvalidToken(_("Token contained no recognizable user identification"))

        try:
            operator = FactoryOperator.objects.get(id=operator_id)
        except FactoryOperator.DoesNotExist:
            raise AuthenticationFailed(_("Factory Operator not found"), code="operator_not_found")
            
        try:
            FactoryOperatorSession.objects.get(id=session_id, operator=operator)
        except FactoryOperatorSession.DoesNotExist:
            raise AuthenticationFailed(_("Session is invalid or expired"), code="session_invalid")

        return operator
