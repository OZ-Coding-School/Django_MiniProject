from .base import *

DEBUG = True

ALLOWED_HOSTS = []

ROOT_URLCONF = "config.dev_urls"

INSTALLED_APPS += [
    'drf_yasg',
]

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