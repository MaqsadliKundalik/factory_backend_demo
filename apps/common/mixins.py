from rest_framework.viewsets import ModelViewSet
from apps.common.permissions import HasDynamicPermission
from drf_yasg.utils import swagger_auto_schema
from apps.common.filters import DATE_FILTER_PARAMS

class DateFilterSchemaMixin:
    """
    Swagger da start_date va end_date filterlarini ko'rsatish uchun mixin.
    Bu mixin list() va boshqa amallarni dekoratsiya qiladi.
    """
    @swagger_auto_schema(manual_parameters=DATE_FILTER_PARAMS)
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)


class PermissionMetaMixin:
    """
    Mixin to add permission metadata to the response.
    """
    def finalize_response(self, request, response, *args, **kwargs):
        # Only add meta for successful dictionary responses
        if (200 <= response.status_code < 300) and isinstance(response.data, dict):
            permissions_meta = self.get_permissions_meta(request)
            if permissions_meta:
                # Add 'meta' to the response data
                # Using a fresh dict to ensure 'meta' is at the top level even in paginated responses
                if 'results' in response.data:
                    # It's a paginated list
                    response.data['meta'] = permissions_meta
                else:
                    # It's a single object or non-paginated list
                    response.data['meta'] = permissions_meta
        
        return super().finalize_response(request, response, *args, **kwargs)

    def get_permissions_meta(self, request):
        meta = {
            "can_access": True # Foydalanuvchi bu yerda bo'lsa, demak ruxsat bor
        }
        
        permission_classes = getattr(self, 'permission_classes', [])
        for perm_class in permission_classes:
            perm_instance = perm_class() if callable(perm_class) else perm_class
            
            if isinstance(perm_instance, HasDynamicPermission):
                crud_perm = perm_instance.crud_perm
                read_perm = perm_instance.read_perm
                
                if crud_perm:
                    meta['can_edit'] = request.user.has_perm(crud_perm)
                if read_perm:
                    meta['can_read'] = request.user.has_perm(read_perm)
        
        return meta
