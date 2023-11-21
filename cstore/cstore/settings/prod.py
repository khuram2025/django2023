from .base import *
from pathlib import Path
import os

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Database
# https://docs.djangoproject.com/en/4.0/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'channabdb',
        'USER': 'channab',
        'PASSWORD': 'Read@123',
        'HOST': 'localhost',  # Or the IP address of your PostgreSQL server
        'PORT': '5432',
    }
}


STATIC_URL = '/static/'
STATIC_ROOT = '/home/ubuntu/Django2023/cstore/static/'
