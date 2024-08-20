from .base import *

DEBUG = False

ALLOWED_HOSTS = []

ROOT_URLCONF = "config.urls"

# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'HOST': SECRET['POSTGRES']['HOST'],
        'USER': SECRET['POSTGRES']['USER'],
        'PASSWORD': SECRET['POSTGRES']['PASSWORD'],
        'NAME': SECRET['POSTGRES']['NAME'],
        'PORT': 5432,
    }
}