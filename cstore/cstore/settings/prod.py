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



AWS_ACCESS_KEY_ID = 'AKIASTSQA7RFPTLKOHGN'
AWS_SECRET_ACCESS_KEY = '6OJeldWxYS4nc+s0gAMaOamBH1pTpurBEhdfKyGm'
AWS_STORAGE_BUCKET_NAME = 'channabstore'
AWS_S3_REGION_NAME = 'us-east-1'  
AWS_S3_CUSTOM_DOMAIN = '%s.s3.amazonaws.com' % AWS_STORAGE_BUCKET_NAME

DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
MEDIA_URL = 'https://%s/' % AWS_S3_CUSTOM_DOMAIN


STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'collected_static')
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static'),
]
