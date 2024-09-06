from .base import *

DEBUG = True

ALLOWED_HOSTS = []

ROOT_URLCONF = "config.dev_urls"

INSTALLED_APPS += [
    "drf_yasg",
]

# Static
STATIC_URL = "static/"
STATIC_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / ".static_root"

# Media
MEDIA_URL = "media/"
MEDIA_ROOT = BASE_DIR / "media"

# Database
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "HOST": SECRET["POSTGRES"]["HOST"],
        "USER": SECRET["POSTGRES"]["USER"],
        "PASSWORD": SECRET["POSTGRES"]["PASSWORD"],
        "NAME": SECRET["POSTGRES"]["NAME"],
        "PORT": 5432,
    }
}
CELERY_BEAT_SCHEDULE = {
    # 작업 스케줄
    "weekly-analyze-and-notify": {
        "task": "analysis.tasks.weekly_analyze_and_notify_user",
        "schedule": crontab(),
    },
    "monthly-analyze-and-notify": {
        "task": "analysis.tasks.monthly_analyze_and_notify_user",
        "schedule": crontab(),
    },
}
