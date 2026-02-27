from django.shortcuts import render
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from apps.drivers.models import Driver
from apps.drivers.serializers import DriverSerializer
from apps.common.permissions import HasDynamicPermission
from apps.common.auth.authentication import UnifiedJWTAuthentication

class DriverListCreateAPIView(ListCreateAPIView):
    authentication_classes = [UnifiedJWTAuthentication]
    serializer_class = DriverSerializer
    permission_classes = [HasDynamicPermission(crud_perm="crud_driver", read_perm="read_driver")]

    def get_queryset(self):
        user = self.request.user
        if hasattr(user, 'whouses'):
            return Driver.objects.filter(whouse__in=user.whouses.all())
        return Driver.objects.filter(whouse=user.whouse)
        
    def perform_create(self, serializer):
        user = self.request.user
        whouse_id = self.request.data.get('whouse')
        if whouse_id:
            serializer.save(whouse_id=whouse_id)
        else:
            whouse = user.whouses.first() if hasattr(user, 'whouses') else user.whouse
            serializer.save(whouse=whouse)

class DriverRetrieveUpdateDestroyAPIView(RetrieveUpdateDestroyAPIView):
    authentication_classes = [UnifiedJWTAuthentication]
    serializer_class = DriverSerializer
    permission_classes = [HasDynamicPermission(crud_perm="crud_driver", read_perm="read_driver")]

    def get_queryset(self):
        user = self.request.user
        return Driver.objects.filter(whouse=user.whouse)
