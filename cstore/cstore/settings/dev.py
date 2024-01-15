# dev.py settings

from .base import *

# Database
# https://docs.djangoproject.com/en/4.0/ref/settings/#databases

# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.sqlite3',
#         'NAME': BASE_DIR / 'db.sqlite3',
#     }
# }

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'devdb',
        'USER': 'postgres',
        'PASSWORD': 'Read@123',
        'HOST': 'localhost',  # Or the IP address of your PostgreSQL server
        'PORT': '5432',
    }
}

