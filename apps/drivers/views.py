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
        return Driver.objects.filter(whouse=user.whouse)
        
    def perform_create(self, serializer):
        serializer.save(whouse=self.request.user.whouse)

class DriverRetrieveUpdateDestroyAPIView(RetrieveUpdateDestroyAPIView):
    authentication_classes = [UnifiedJWTAuthentication]
    serializer_class = DriverSerializer
    permission_classes = [HasDynamicPermission(crud_perm="crud_driver", read_perm="read_driver")]

    def get_queryset(self):
        user = self.request.user
        return Driver.objects.filter(whouse=user.whouse)
