import os
from .common import *


# WHEN DEBUG = False, Django doesn't work at all without a suitable value for ALLOWED_HOSTS
DEBUG = False

SECRET_KEY = os.environ['SECRET_KEY']

# YOu need to populate this for production
ALLOWED_HOSTS = []
