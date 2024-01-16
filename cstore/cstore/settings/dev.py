# dev.py settings

from .base import *

# Database
# https://docs.djangoproject.com/en/4.0/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


ELASTICSEARCH_DSL = {
    'default': {
        'hosts': 'http://localhost:9200'  # or 'https://localhost:9200' if using https
    },
}


INSTALLED_APPS += ['django_elasticsearch_dsl']