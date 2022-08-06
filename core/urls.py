from django.views.generic import TemplateView
from django.urls import path
from . import views

urlpatterns = [
    # we added the core folder to avoid having name colissions with other index.html files
    path('', TemplateView.as_view(template_name='core/index.html')),
]
