from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import AuthenticationFailed, InvalidToken
from django.utils.translation import gettext_lazy as _
from apps.whouse_manager.models import WhouseManager
from apps.factory_operator.models import FactoryOperator
from apps.drivers.models import Driver
from apps.guard.models import Guard
from apps.session.models import WhouseManagerSession, FactoryOperatorSession, DriverSession, GuardSession

class UnifiedJWTAuthentication(JWTAuthentication):
    def get_user(self, validated_token):
        try:
            user_id = validated_token["user_id"]
            role = validated_token["role"]
            session_id = validated_token["session"]
        except KeyError:
            raise InvalidToken(_("Token contained no recognizable user identification"))

        if role == "manager":
            return self._authenticate_manager(user_id, session_id)
        elif role == "operator":
            return self._authenticate_operator(user_id, session_id)
        elif role == "driver":
            return self._authenticate_driver(user_id, session_id)
        elif role == "guard":
            return self._authenticate_guard(user_id, session_id)
        else:
            raise AuthenticationFailed(_("Invalid user role"), code="role_invalid")

    def _authenticate_manager(self, user_id, session_id):
        try:
            manager = WhouseManager.objects.get(id=user_id)
        except WhouseManager.DoesNotExist:
            raise AuthenticationFailed(_("Manager not found"), code="user_not_found")
        
        if not WhouseManagerSession.objects.filter(id=session_id, whouse_manager=manager).exists():
            raise AuthenticationFailed(_("Session is invalid or expired"), code="session_invalid")
        
        return manager

    def _authenticate_operator(self, user_id, session_id):
        try:
            operator = FactoryOperator.objects.get(id=user_id)
        except FactoryOperator.DoesNotExist:
            raise AuthenticationFailed(_("Factory Operator not found"), code="user_not_found")
            
        if not FactoryOperatorSession.objects.filter(id=session_id, operator=operator).exists():
            raise AuthenticationFailed(_("Session is invalid or expired"), code="session_invalid")

        return operator

    def _authenticate_driver(self, user_id, session_id):
        try:
            driver = Driver.objects.get(id=user_id)
        except Driver.DoesNotExist:
            raise AuthenticationFailed(_("Driver not found"), code="user_not_found")
            
        if not DriverSession.objects.filter(id=session_id, driver=driver).exists():
            raise AuthenticationFailed(_("Session is invalid or expired"), code="session_invalid")

        return driver

    def _authenticate_guard(self, user_id, session_id):
        try:
            guard = Guard.objects.get(id=user_id)
        except Guard.DoesNotExist:
            raise AuthenticationFailed(_("Guard not found"), code="user_not_found")
            
        if not GuardSession.objects.filter(id=session_id, guard=guard).exists():
            raise AuthenticationFailed(_("Session is invalid or expired"), code="session_invalid")

        return guard
