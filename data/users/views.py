from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from itertools import chain
from apps.drivers.models import Driver
from apps.guard.models import Guard
from apps.factory_operator.models import FactoryOperator
from apps.whouse_manager.models import WhouseManager
from .serializers import UnifiedUserSerializer
from apps.common.auth.authentication import UnifiedJWTAuthentication
from rest_framework.permissions import IsAuthenticated

class UserListPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100

class UnifiedUserListView(APIView):
    authentication_classes = [UnifiedJWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        whouse_id = request.query_params.get('whouse')
        
        # Aggregate querysets
        managers = WhouseManager.objects.all().order_by('-created_at')
        operators = FactoryOperator.objects.all().order_by('-created_at')
        drivers = Driver.objects.all().order_by('-created_at')
        guards = Guard.objects.all().order_by('-created_at')

        # Filter by whouse if provided
        if whouse_id:
            managers = managers.filter(whouses__id=whouse_id)
            operators = operators.filter(whouse__id=whouse_id)
            drivers = drivers.filter(whouse__id=whouse_id)
            guards = guards.filter(whouse__id=whouse_id)

        # Combine as a list
        combined_users = sorted(
            chain(managers, operators, drivers, guards),
            key=lambda x: x.created_at,
            reverse=True
        )

        paginator = UserListPagination()
        paginated_users = paginator.paginate_queryset(combined_users, request, view=self)
        
        serializer = UnifiedUserSerializer(paginated_users, many=True)
        return paginator.get_paginated_response(serializer.data)
