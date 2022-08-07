"""storefront URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView

# Change the header of the admin dashboard
admin.site.site_header = 'Storefront Admin'
admin.site.index_title = 'Admin'

# The difference between jwt and token authentication is:
# toekn authentication saves tokens in the database so every request will have to make a call to the database
# Json Web Tokens does not rely on the database, it uses a digital signature to verify the token
# In this course we are going ot use JWT. Let's see what they use at Ford

urlpatterns = [
    # '' refers to the root of the website
    path('', include('core.urls')),
    path('admin/', admin.site.urls),
    path('react/', TemplateView.as_view(template_name='index.html')),
    path('playground/', include('playground.urls')),
    path('store/', include('store.urls')),
    path('auth/', include('djoser.urls')),
    path('auth/', include('djoser.urls.jwt')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# What we are telling django here is that any request that comes to /media/ should be routed to the folder  /media/
