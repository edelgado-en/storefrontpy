from django_filters.rest_framework import FilterSet
from .models import Product


class ProductFilter(FilterSet):
    class Meta:
        model = Product
        # for more details and options you need to read the documentation
        # You can also use a SearchFilter instead of this
        fields = {
            'title': ['icontains'],
        }
