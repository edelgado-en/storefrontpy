import os
from .common import *


# WHEN DEBUG = False, Django doesn't work at all without a suitable value for ALLOWED_HOSTS
DEBUG = False

# To generate a secret key, go to djecrety.ir
# set the environt variable in heroku
# in the terminal: heroku config:set SECRET_KEY='<your_secret_key>'
# The Django secret key is used to provide cyptographic signing. This key is mostly used to sign session cookies.
# If one were to have this key, they would be able to modify the cookies sent by the application.
SECRET_KEY = os.environ['SECRET_KEY']

# Then you need to set the DJANGO_SETTINGS_MODULE environment variable to the storefront.settings.prod module.
# in the terminal: heroku config:set DJANGO_SETTINGS_MODULE='storefront.settings.prod'

# YOu need to populate this for production
# Notice how we don't include http or slashes in the hostname.. We just need the hostname
ALLOWED_HOSTS = ['store-edelgado-prod.herokuapp.com']

# in the DATABASE_URL provided by Heroku, the username and password are included in the database url and it is encrypted
# In Datagrip, you need to change from default to url only so that you don't have to enter username and password
