from django.contrib import admin
from django.db.models.aggregates import Count
from . import models

# The name of this class can be anything but the convention is ModelNameAdmin


@admin.register(models.Product)
class ProductAdmin(admin.ModelAdmin):
    # You can add computed columns as well like inventory_status
    list_display = ['title', 'price', 'inventory_status']
    list_editable = ['price']
    list_per_page = 10

    @admin.display(ordering='inventory')
    def inventory_status(self, product):
        return 'Ok' if product.inventory > 10 else 'Low'

# You can add more classes for each of the models


# Register your models here.
# admin.site.register(models.Collection)
@admin.register(models.Collection)
class CollectionAdmin(admin.ModelAdmin):
    list_display = ['title', 'products_count']

    # custom column
    @admin.display(ordering='products_count')
    def products_count(self, collection):
        return collection.products_count

    def get_queryset(self, request):
        return super().get_queryset(request).annotate(
            products_count=Count('products')
        )

# This is not needed because I"m using the decorator @admin.register
# admin.site.register(models.Product)


@admin.register(models.Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ['first_name', 'last_name', 'membership', 'get_orders']
