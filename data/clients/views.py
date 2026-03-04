from rest_framework.viewsets import ModelViewSet
from .models import Client, ClientBranches
from .serializers import ClientSerializer, ClientBranchesSerializer, ClientAndBranchesBulkSerializer
from drf_yasg.utils import swagger_auto_schema
from apps.common.auth.authentication import UnifiedJWTAuthentication
from apps.common.permissions import HasDynamicPermission
from apps.common.filters import BaseDateFilterSet
from rest_framework.views import APIView
from rest_framework.response import Response
from django.db import transaction
from rest_framework import status
from apps.common.mixins import PermissionMetaMixin, DateFilterSchemaMixin
from rest_framework.pagination import PageNumberPagination
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter

class StandardResultsSetPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100

class ClientFilter(BaseDateFilterSet):
    class Meta:
        model = Client
        fields = ['whouse', 'created_at', 'updated_at']

class ClientBranchesFilter(BaseDateFilterSet):
    class Meta:
        model = ClientBranches
        fields = ['client']

class ClientViewSet(DateFilterSchemaMixin, PermissionMetaMixin, ModelViewSet):
    queryset = Client.objects.all()
    serializer_class = ClientSerializer
    authentication_classes = [UnifiedJWTAuthentication]
    permission_classes = [HasDynamicPermission(crud_perm="CLIENTS_PAGE", read_perm="CLIENTS_PAGE")]
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = ClientFilter
    search_fields = ['name', 'phone_number']
    ordering_fields = ['created_at', 'updated_at']

    def get_queryset(self):
        user = self.request.user
        if getattr(self, 'swagger_fake_view', False) or not user.is_authenticated:
            return Client.objects.none()

        whouses = user.whouses.all()
        return Client.objects.filter(whouse__in=whouses)

    def perform_create(self, serializer):
        user = self.request.user
        whouse_id = self.request.data.get('whouse')
        if whouse_id:
            serializer.save(whouse_id=whouse_id)
        else:
            whouse = user.whouses.first()
            serializer.save(whouse=whouse)

class ClientBranchesViewSet(DateFilterSchemaMixin, PermissionMetaMixin, ModelViewSet):
    queryset = ClientBranches.objects.all()
    serializer_class = ClientBranchesSerializer
    authentication_classes = [UnifiedJWTAuthentication]
    permission_classes = [HasDynamicPermission(crud_perm="CLIENTS_PAGE", read_perm="CLIENTS_PAGE")]
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = ClientBranchesFilter
    search_fields = ['name', 'address']
    ordering_fields = ['created_at', 'updated_at']

    def get_queryset(self):
        user = self.request.user
        if getattr(self, 'swagger_fake_view', False) or not user.is_authenticated:
            return ClientBranches.objects.none()

        return ClientBranches.objects.all()


class ClientAndBranchesCreateUpdateView(APIView):
    authentication_classes = [UnifiedJWTAuthentication]
    permission_classes = [HasDynamicPermission(crud_perm="CLIENTS_PAGE", read_perm="CLIENTS_PAGE")]

    @swagger_auto_schema(
        operation_summary="Create client and branches",
        request_body=ClientAndBranchesBulkSerializer,
        responses={201: ClientSerializer}
    )
    @transaction.atomic
    def post(self, request):
        user = request.user
        data = request.data.copy()
        
        # Whouse handling
        if not data.get('whouse'):
            whouse = user.whouses.first()
            if whouse:
                data['whouse'] = whouse.id
        
        client_serializer = ClientSerializer(data=data)
        client_serializer.is_valid(raise_exception=True)
        client = client_serializer.save()
        
        branches_data = data.get('branches', [])
        for branch_item in branches_data:
            branch_item['client'] = client.id
            branch_serializer = ClientBranchesSerializer(data=branch_item)
            branch_serializer.is_valid(raise_exception=True)
            branch_serializer.save()
            
        return Response(ClientSerializer(client).data, status=status.HTTP_201_CREATED)

