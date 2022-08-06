from django.urls import path
from . import views

# django looks for the name urlpatterns

urlpatterns = [
    path('hello/', views.HelloView.as_view()),
]
