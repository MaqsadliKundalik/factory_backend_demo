from django.shortcuts import render
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from apps.drivers.models import Driver
from apps.drivers.serializers import DriverSerializer, DriverPasswordChangeSerializer
from apps.common.permissions import HasDynamicPermission
from apps.common.auth.authentication import UnifiedJWTAuthentication
from rest_framework.pagination import PageNumberPagination
from apps.common.filters import BaseDateFilterSet
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter


class StandardResultsSetPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100

class DriverFilter(BaseDateFilterSet):
    class Meta:
        model = Driver
        fields = ['whouse', 'created_at', 'updated_at']


class DriverListCreateAPIView(ListCreateAPIView):
    authentication_classes = [UnifiedJWTAuthentication]
    serializer_class = DriverSerializer
    permission_classes = [HasDynamicPermission(crud_perm="TRANSPORTS_PAGE", read_perm="TRANSPORTS_PAGE")]
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = DriverFilter
    search_fields = ['name', 'phone_number']
    ordering_fields = ['created_at', 'updated_at']
    
    def get_queryset(self):
        user = self.request.user
        if getattr(self, 'swagger_fake_view', False) or not user.is_authenticated:
            return Driver.objects.none()

        whouses = user.whouses.all()
        return Driver.objects.filter(whouse__in=whouses)
        
    def perform_create(self, serializer):
        user = self.request.user
        whouse_id = self.request.data.get('whouse')
        if whouse_id:
            serializer.save(whouse_id=whouse_id)
        else:
            whouse = user.whouses.first()
            serializer.save(whouse=whouse)

class DriverRetrieveUpdateDestroyAPIView(RetrieveUpdateDestroyAPIView):
    authentication_classes = [UnifiedJWTAuthentication]
    serializer_class = DriverSerializer
    permission_classes = [HasDynamicPermission(crud_perm="TRANSPORTS_PAGE", read_perm="TRANSPORTS_PAGE")]

    def get_queryset(self):
        user = self.request.user
        if getattr(self, 'swagger_fake_view', False) or not user.is_authenticated:
            return Driver.objects.none()

        whouses = user.whouses.all()
        return Driver.objects.filter(whouse__in=whouses)


class DriverPasswordChangeView(APIView):
    authentication_classes = [UnifiedJWTAuthentication]
    permission_classes = [HasDynamicPermission(crud_perm="DRIVERS_PAGE", read_perm="DRIVERS_PAGE")]

    @swagger_auto_schema(
        operation_summary="Изменение пароля водителя",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['new_password'],
            properties={
                'new_password': openapi.Schema(type=openapi.TYPE_STRING, description='Новый пароль'),
            }
        ),
        responses={
            200: "Пароль успешно изменен",
            400: "Неверные данные",
            404: "Водитель не найден",
        }
    )
    def post(self, request, driver_id):
        try:
            user = request.user
            if getattr(self, 'swagger_fake_view', False) or not user.is_authenticated:
                return Response({"error": "Требуется аутентификация"}, status=status.HTTP_401_UNAUTHORIZED)

            # Faqat o'zining parolini o'zgartirishi mumkin yoki admin bo'lishi kerak
            if user.__class__.__name__ == 'Driver' and str(user.id) != str(driver_id):
                return Response({"error": "Вы можете изменить только свой пароль"}, status=status.HTTP_403_FORBIDDEN)

            # Warehousega tegishli driverlarni filterlash
            whouses = user.whouses.all()
            driver = Driver.objects.filter(id=driver_id, whouse__in=whouses).first()
            
            if not driver:
                return Response({"error": "Водитель не найден"}, status=status.HTTP_404_NOT_FOUND)

            serializer = DriverPasswordChangeSerializer(
                data=request.data, 
                context={'driver': driver}
            )
            
            if serializer.is_valid():
                serializer.save()
                return Response({"message": "Пароль успешно изменен"}, status=status.HTTP_200_OK)
            
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
