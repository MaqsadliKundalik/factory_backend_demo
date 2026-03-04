from django_filters import rest_framework as filters
from drf_yasg import openapi

class BaseDateFilterSet(filters.FilterSet):
    start_date = filters.DateFilter(field_name="created_at", lookup_expr='date__gte')
    end_date = filters.DateFilter(field_name="created_at", lookup_expr='date__lte')

    class Meta:
        fields = []

DATE_FILTER_PARAMS = [
    openapi.Parameter(
        'start_date', openapi.IN_QUERY,
        description="Boshlang'ich sana (YYYY-MM-DD)",
        type=openapi.TYPE_STRING, format=openapi.FORMAT_DATE,
        required=False,
    ),
    openapi.Parameter(
        'end_date', openapi.IN_QUERY,
        description="Tugash sanasi (YYYY-MM-DD)",
        type=openapi.TYPE_STRING, format=openapi.FORMAT_DATE,
        required=False,
    ),
]
