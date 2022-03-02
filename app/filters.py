import django_filters
from django_filters import DateFilter
from .models import *

class OrderFilter(django_filters.FilterSet):
    # start_date = DateFilter(field_name='date',lookup_expr='gte')
    # end_date = DateFilter(field_name='date',lookup_expr='lte')
    class Meta:
        model = User
        fields = ['docket_no','name','city']