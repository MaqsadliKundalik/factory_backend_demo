from django_filters import rest_framework as filters

class BaseDateFilterSet(filters.FilterSet):
    start_date = filters.DateFilter(field_name="created_at", lookup_expr='date__gte')
    end_date = filters.DateFilter(field_name="created_at", lookup_expr='date__lte')

    class Meta:
        fields = []
