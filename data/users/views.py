from rest_framework.viewsets import ViewSet
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from rest_framework import status
from django.shortcuts import get_object_or_404
from itertools import chain
from apps.drivers.models import Driver
from apps.guard.models import Guard
from apps.factory_operator.models import FactoryOperator
from apps.whouse_manager.models import WhouseManager
from .serializers import UnifiedUserSerializer
from apps.common.auth.authentication import UnifiedJWTAuthentication
from rest_framework.permissions import IsAuthenticated
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

class UserListPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100

class UnifiedUserViewSet(ViewSet):
    authentication_classes = [UnifiedJWTAuthentication]
    permission_classes = [IsAuthenticated]
    pagination_class = UserListPagination
    serializer_class = UnifiedUserSerializer

    def _get_all_users_queryset(self, whouse_id=None):
        managers = WhouseManager.objects.all().order_by('-created_at')
        operators = FactoryOperator.objects.all().order_by('-created_at')
        drivers = Driver.objects.all().order_by('-created_at')
        guards = Guard.objects.all().order_by('-created_at')

        if whouse_id:
            managers = managers.filter(whouses__id=whouse_id)
            operators = operators.filter(whouse__id=whouse_id)
            drivers = drivers.filter(whouse__id=whouse_id)
            guards = guards.filter(whouse__id=whouse_id)

        return sorted(
            chain(managers, operators, drivers, guards),
            key=lambda x: x.created_at,
            reverse=True
        )

    @swagger_auto_schema(
        operation_summary="List all users",
        operation_description="Returns a paginated list of all users from all roles (Manager, Operator, Driver, Guard).",
        manual_parameters=[
            openapi.Parameter(
                'whouse', 
                openapi.IN_QUERY, 
                description="Filter users by Warehouse ID", 
                type=openapi.TYPE_STRING,
                format=openapi.FORMAT_UUID
            ),
        ],
        responses={200: UnifiedUserSerializer(many=True)}
    )
    def list(self, request):
        whouse_id = request.query_params.get('whouse')
        combined_users = self._get_all_users_queryset(whouse_id)
        
        paginator = self.pagination_class()
        paginated_users = paginator.paginate_queryset(combined_users, request, view=self)
        
        serializer = UnifiedUserSerializer(paginated_users, many=True)
        return paginator.get_paginated_response(serializer.data)

    @swagger_auto_schema(
        operation_summary="Create a new user",
        operation_description="Create a new user and map it to the correct role model based on the 'role' field.",
        request_body=UnifiedUserSerializer,
        responses={201: UnifiedUserSerializer()}
    )
    def create(self, request):
        serializer = UnifiedUserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def _get_instance(self, pk):
        # Try finding in each model
        for model in [WhouseManager, FactoryOperator, Driver, Guard]:
            instance = model.objects.filter(id=pk).first()
            if instance:
                return instance
        return None

    @swagger_auto_schema(
        operation_summary="Retrieve a user",
        operation_description="Retrieve details of a specific user by its ID.",
        responses={200: UnifiedUserSerializer()}
    )
    def retrieve(self, request, pk=None):
        instance = self._get_instance(pk)
        if not instance:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)
        serializer = UnifiedUserSerializer(instance)
        return Response(serializer.data)

    @swagger_auto_schema(
        operation_summary="Update a user",
        operation_description="Update details of a specific user. Note: Role cannot be changed via update.",
        request_body=UnifiedUserSerializer,
        responses={200: UnifiedUserSerializer()}
    )
    def update(self, request, pk=None):
        instance = self._get_instance(pk)
        if not instance:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)
        serializer = UnifiedUserSerializer(instance, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        operation_summary="Partial update a user",
        operation_description="Partially update details of a specific user.",
        request_body=UnifiedUserSerializer,
        responses={200: UnifiedUserSerializer()}
    )
    def partial_update(self, request, pk=None):
        instance = self._get_instance(pk)
        if not instance:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)
        serializer = UnifiedUserSerializer(instance, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        operation_summary="Delete a user",
        operation_description="Delete a specific user from the system.",
        responses={204: "Successfully deleted"}
    )
    def destroy(self, request, pk=None):
        instance = self._get_instance(pk)
        if not instance:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)
        instance.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
