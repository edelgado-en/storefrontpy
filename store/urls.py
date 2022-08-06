from django.urls import path, include
from rest_framework.routers import SimpleRouter, DefaultRouter
from rest_framework_nested import routers
from . import views

# django looks for the name urlpatterns

router = DefaultRouter()
# it seems like using viewsets is better because it is less code. We will see.
router.register('carts', views.CartViewSet)
router.register('customers', views.CustomerViewSet)
# basename: The base to use for the URL names that are created. If unset the basename will be automatically
# generated based on the queryset attribute of the viewset, if it has one. Note that if the viewset does not include a
# queryset attribute then you must set basename when registering the viewset.
router.register('orders', views.OrderViewSet, basename='orders')

# because we have a nested route for cart/eqwewqeqwe/items, we need a nested router
carts_router = routers.NestedDefaultRouter(router, 'carts', lookup='cart')
carts_router.register('items', views.CartItemViewSet, basename='cart-items')

urlpatterns = [
    # .as_view() converts the ProductView class to a function that takes a request and returns a response
    path('products/', views.ProductView.as_view()),
    # you can apply a converter (int:) to make sure the id is an integer
    path('products/<int:pk>/', views.ProductDetail.as_view()),
    path('collections/', views.CollectionList.as_view()),
    path('collections/<int:pk>/', views.CollectionDetail.as_view()),
    path('', include(router.urls)),
    path('', include(carts_router.urls))
]
