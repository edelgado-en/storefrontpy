from .common import *

DEBUG = True

SECRET_KEY = 'django-insecure-aqu*58h#6&7cl_%u^_)o@$(lgs4mwrjk7b1d(tc1lxv#=v@)$!'

# Database
# https://docs.djangoproject.com/en/4.0/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'storefront',
        'HOST': 'localhost',
        'USER': 'root',
        'PASSWORD': 'root',
    }
}
