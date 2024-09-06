import json
import os
import random
from datetime import timedelta
from pathlib import Path

from celery.schedules import crontab

BASE_DIR = Path(__file__).resolve().parent.parent.parent

# 환경변수 가져오기
try:
    with open(BASE_DIR / "secret.json") as f:
        config_secret_str = f.read()
    SECRET = json.loads(config_secret_str)
# CI 용
except FileNotFoundError:
    SECRET = {
        "DJANGO_SECRET_KEY": "".join(random.choices("abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*()?", k=50)),
        "POSTGRES": {"HOST": "localhost", "USER": "postgres", "PASSWORD": "postgres", "NAME": "django", "PORT": 5432},
    }

SECRET_KEY = SECRET["DJANGO_SECRET_KEY"]

# Application definition
# installed app
DJANGO_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
]

CUSTOM_APPS = [
    "users",
    "accounts",
    "transactions",
    "analysis",
    "notifications",
    "core",
]

THIRD_PARTY_APPS = [
    "django_extensions",
    "rest_framework",
    "celery",
    "django_celery_beat",
    "django_celery_results",
]

INSTALLED_APPS = DJANGO_APPS + CUSTOM_APPS + THIRD_PARTY_APPS

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

# Internationalization
LANGUAGE_CODE = "ko-kr"
TIME_ZONE = "Asia/Seoul"
USE_I18N = True
USE_TZ = True

# Default primary key field type
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Auth
AUTH_USER_MODEL = "users.User"

# SIMPLE JWT
SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=60 * 2),  # 2 hours
    "REFRESH_TOKEN_LIFETIME": timedelta(days=1),  # 1 day
    "UPDATE_LAST_LOGIN": True,
    "ALGORITHM": "HS256",
    "TOKEN_TYPE_CLAIM": "token_type",
    "TOKEN_USER_CLASS": "rest_framework_simplejwt.tokens.User",
}

# oauth
if SECRET.get("KAKAO"):
    KAKAO_CLIENT_ID = SECRET["KAKAO"]["CLIENT_ID"]
    KAKAO_CLIENT_SECRET = SECRET["KAKAO"]["CLIENT_SECRET"]
else:
    KAKAO_CLIENT_ID = os.environ.get("KAKAO_CLIENT_ID")
    KAKAO_CLIENT_SECRET = os.environ.get("KAKAO_CLIENT_SECRET")
KAKAO_CALLBACK_URL = "/users/oauth/kakao/callback/"

if SECRET.get("GOOGLE"):
    GOOGLE_CLIENT_ID = SECRET["GOOGLE"]["CLIENT_ID"]
    GOOGLE_CLIENT_SECRET = SECRET["GOOGLE"]["CLIENT_SECRET"]
else:
    GOOGLE_CLIENT_ID = os.environ.get("GOOGLE_CLIENT_ID")
    GOOGLE_CLIENT_SECRET = os.environ.get("GOOGLE_CLIENT_SECRET")
GOOGLE_CALLBACK_URL = "/users/oauth/google/callback/"

if SECRET.get("NAVER"):
    NAVER_CLIENT_ID = SECRET["NAVER"]["CLIENT_ID"]
    NAVER_CLIENT_SECRET = SECRET["NAVER"]["CLIENT_SECRET"]
else:
    NAVER_CLIENT_ID = os.environ.get("NAVER_CLIENT_ID")
    NAVER_CLIENT_SECRET = os.environ.get("NAVER_CLIENT_SECRET")
NAVER_CALLBACK_URL = "/users/oauth/naver/callback/"

# REST FRAMEWORK
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
        "rest_framework.authentication.SessionAuthentication",
    ),
    "DEFAULT_PERMISSION_CLASSES": ("rest_framework.permissions.IsAuthenticated",),
}

# EMAIL
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = "smtp.naver.com"
EMAIL_PORT = 587
if SECRET.get("EMAIL"):
    EMAIL_HOST_USER = SECRET["EMAIL"]["USER"]
    EMAIL_HOST_PASSWORD = SECRET["EMAIL"]["PASSWORD"]
else:
    EMAIL_HOST_USER = os.environ.get("EMAIL_USER")
    EMAIL_HOST_PASSWORD = os.environ.get("EMAIL_PASSWORD")
EMAIL_USE_TLS = True
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER

# Celery 설정
CELERY_BROKER_URL = 'redis://localhost:6379/0'  # 데이터베이스를 브로커로 사용
CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'  # 작업 결과를 데이터베이스에 저장
CELERY_ACCEPT_CONTENT = ['application/json']
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TASK_SERIALIZER = 'json'
CELERY_BEAT_SCHEDULER = 'django_celery_beat.schedulers:DatabaseScheduler'
CELERY_TIMEZONE = 'Asia/Seoul'
