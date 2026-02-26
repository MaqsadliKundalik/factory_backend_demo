from rest_framework.permissions import BasePermission
from apps.whouse_manager.models import WhouseManager
from apps.factory_operator.models import FactoryOperator
from apps.drivers.models import Driver

class IsWhouseManager(BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and isinstance(request.user, WhouseManager))

class IsFactoryOperator(BasePermission):

    def has_permission(self, request, view):
        return bool(request.user and isinstance(request.user, FactoryOperator))

class IsDriver(BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and isinstance(request.user, Driver))
    
class IsManagerOrOperator(BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and (isinstance(request.user, WhouseManager) or isinstance(request.user, FactoryOperator)))

class IsOwnerManager(BasePermission):
    def has_object_permission(self, request, view, obj):
        if not bool(request.user and isinstance(request.user, WhouseManager)):
            return False
            
        return request.user.whouse == obj.whouse

class IsOwnerManagerOrOperator(BasePermission):
    def has_object_permission(self, request, view, obj):
        if not bool(request.user and (isinstance(request.user, WhouseManager) or isinstance(request.user, FactoryOperator))):
            return False
            
        return request.user.whouse == obj.whouse
