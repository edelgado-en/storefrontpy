"""
WSGI config for storefront project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.0/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

# WSGI stands for Web Server Gateway Interface. It is a standard interface for a web server to communicate with a web application.
# It is used to forward requests from a web server (such as Apache or Nginx) to a backend Python web application or framework.
# Most Python frameworks include a basic development server that can be used while building your web application.
# When you are ready to go live from a staging to a production environment, most deployments will utilize WSGI.

# wsgi is pronounced whisky

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'storefront.settings.dev')

# when starting the applicaiton using gunicorn, we need to specify this file as the entry point
# to start server: type in the terminal gunicorn storefront.wsgi

# gunicorn is WAY FASTER THAN THE DEVELOPMENT SERVER. Gunicorn is for production use.

# in development mode, you use python3 manage.py runserver

application = get_wsgi_application()
