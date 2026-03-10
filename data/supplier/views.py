from rest_framework.viewsets import ModelViewSet
from rest_framework.pagination import PageNumberPagination
from rest_framework.filters import SearchFilter
from rest_framework.views import APIView
from django.db import transaction
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from django_filters.rest_framework import DjangoFilterBackend
from django_filters import rest_framework as filters
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from apps.common.auth.authentication import UnifiedJWTAuthentication
from apps.common.permissions import HasDynamicPermission
from apps.common.mixins import PermissionMetaMixin
from apps.common.filters import BaseDateFilterSet, DATE_FILTER_PARAMS

from .models import Supplier, SupplierPhone
from .serializers import SupplierSerializer, SupplierPhoneSerializer, SupplierBulkSerializer, SelectSupplierSerializer

SUPPLIER_FILTER_PARAMS = DATE_FILTER_PARAMS + [
    openapi.Parameter('whouse', openapi.IN_QUERY, type=openapi.TYPE_STRING, description="Warehouse ID"),
]

class StandardResultsSetPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100

class SupplierFilter(BaseDateFilterSet):
    class Meta:
        model = Supplier
        fields = ['whouse', 'name', 'inn_number']

class SupplierViewSet(PermissionMetaMixin, ModelViewSet):
    queryset = Supplier.objects.all()
    serializer_class = SupplierSerializer
    authentication_classes = [UnifiedJWTAuthentication]
    permission_classes = [HasDynamicPermission(crud_perm="CLIENTS_PAGE", read_perm="CLIENTS_PAGE")]
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_class = SupplierFilter
    search_fields = ['name', 'inn_number']

    def get_queryset(self):
        user = self.request.user
        if getattr(self, 'swagger_fake_view', False) or not user.is_authenticated:
            return Supplier.objects.none()
        
        if hasattr(user, 'whouses') and user.whouses.exists():
            return Supplier.objects.filter(whouse__in=user.whouses.all())
        return Supplier.objects.all()

    def perform_create(self, serializer):
        user = self.request.user
        whouse_id = self.request.data.get('whouse')
        if whouse_id:
            serializer.save(whouse_id=whouse_id)
        else:
            whouse = user.whouses.first()
            serializer.save(whouse=whouse)

class SupplierAndPhoneCreateView(APIView):
    authentication_classes = [UnifiedJWTAuthentication]
    permission_classes = [HasDynamicPermission(crud_perm="CLIENTS_PAGE", read_perm="CLIENTS_PAGE")]

    @swagger_auto_schema(
        operation_summary="Create supplier and phone numbers",
        request_body=SupplierBulkSerializer,
        responses={201: SupplierSerializer}
    )
    @transaction.atomic
    def post(self, request):
        serializer = SupplierBulkSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        supplier = serializer.save()
        return Response(SupplierSerializer(supplier).data, status=status.HTTP_201_CREATED)

class SupplierSelectView(APIView):
    authentication_classes = [UnifiedJWTAuthentication]
    permission_classes = [HasDynamicPermission(crud_perm="CLIENTS_PAGE", read_perm="CLIENTS_PAGE")]

    @swagger_auto_schema(
        operation_summary="Select suppliers (id and name only)",
        responses={200: SelectSupplierSerializer(many=True)},
        manual_parameters=SUPPLIER_FILTER_PARAMS
    )
    @action(detail=False, methods=['get'], pagination_class=None)
    def select(self, request):
        user = self.request.user
        if not user.is_authenticated:
            return Response({"detail": "Not authenticated"}, status=401)
        
        whouses = user.whouses.all()
        queryset = Supplier.objects.filter(whouse__in=whouses)

        # Apply search if provided
        search = request.query_params.get('search')
        if search:
            queryset = queryset.filter(name__icontains=search)
            
        data = queryset.values('id', 'name')
        return Response(list(data))

