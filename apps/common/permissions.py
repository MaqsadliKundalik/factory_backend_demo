from rest_framework.permissions import BasePermission

class HasDynamicPermission(BasePermission):
    def __init__(self, crud_perm=None, read_perm=None):
        self.crud_perm = crud_perm
        self.read_perm = read_perm

    def __call__(self):
        return self

    def has_permission(self, request, view):
        user = request.driver or request.guard or request.operator or request.manager
        if not user or not user.is_authenticated:
            return False
        
        # Determine if this is a read or write operation
        if request.method in ["GET", "HEAD", "OPTIONS"]:
            perm_to_check = self.read_perm or self.crud_perm # Fallback to crud if read not specified
        else:
            perm_to_check = self.crud_perm

        if not perm_to_check:
            return True # If no permission specified, allow

        # Check the boolean field on FactoryUser directly
        return getattr(user, perm_to_check, False)
