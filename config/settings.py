import os
from datetime import timedelta
from pathlib import Path

import dj_database_url
import requests
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.getenv("SECRET_KEY")

DEBUG = True

ALLOWED_HOSTS = ["*"]

INSTALLED_APPS = [
    "jazzmin",
    # base
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # drf
    "rest_framework",
    "rest_framework.authtoken",
    # additional
    "admin_extra_buttons",
    "drf_yasg",
    "ckeditor",
    "ckeditor_uploader",
    "django_filters",
    "corsheaders",
    # celery
    "django_celery_beat",
    "django_celery_results",
    # apps
    "src.account",
    "src.search",
    "src.main",
    "src.bus_tours",
    "src.webhooks",
    "src.notification",
    "src.payment",
    "src.flights",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "debug_toolbar.middleware.DebugToolbarMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [os.path.join(BASE_DIR, "templates")],
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

AUTH_USER_MODEL = "account.User"

LOGIN_REDIRECT_UR = "/admin"

DATABASES = {
    # 'default': dj_database_url.config(default=os.getenv('DATABASE_URL'))
    "default": dj_database_url.config(
        default="postgresql://chyngyz:dpDvaT%23tuJawi4%2BLNU@localhost:5432/hittraveldb"
    )
}


# AUTH_PASSWORD_VALIDATORS = [
#     {
#         "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
#     },
#     {
#         "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
#     },
#     {
#         "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
#     },
#     {
#         "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
#     },
# ]


LANGUAGE_CODE = "ru"

TIME_ZONE = "Asia/Bishkek"

USE_I18N = True

USE_TZ = True

""" Media and Static files
"""
STATIC_URL = "/static/"

STATIC_ROOT = os.path.join(BASE_DIR, "static")


MEDIA_URL = "/media/"
MEDIA_ROOT = os.path.join(BASE_DIR, "media")

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"


""" App settings
"""
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework.authentication.TokenAuthentication",
        "rest_framework.authentication.SessionAuthentication",
    ],
    "DEFAULT_FILTER_BACKENDS": ["django_filters.rest_framework.DjangoFilterBackend"],
}

CORS_ALLOWED_ORIGINS = [
    # "https://hittravel.vercel.app",
    "https://testibank.cbk.kg",
]

CSRF_TRUSTED_ORIGINS = [
    # "https://hittravel.vercel.app",
    "https://hit-travel.org",
]

CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://127.0.0.1:6379/1",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        },
    }
}

CORS_ALLOW_METHODS = ("GET", "OPTIONS", "PATCH", "POST", "PUT", "DELETE")


JAZZMIN_SETTINGS = {
    "site_title": "Hit-Travel",
    "site_header": "Hit-Travel",
    "site_brand": "Hit-Travel",
    "site_logo": "hit-logo.png",
    "site_logo_classes": "img",
    "show_ui_builder": True,
    "icons": {
        "account": "fas fa-users-cog",
        "account.user": "fas fa-user",
        "auth.Group": "fas fa-users",
        "search.favorites": "fas fa-heart",
    },
}

""" Global variables
"""
EMAIL_USE_TLS = True
EMAIL_HOST = "smtp.gmail.com"
EMAIL_PORT = 587
EMAIL_HOST_USER = os.getenv("EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD = os.getenv("EMAIL_HOST_PASSWORD")

AUTHLOGIN = os.getenv("AUTHLOGIN")
AUTHPASS = os.getenv("AUTHPASS")
KEY = os.getenv("KEY")

CKEDITOR_CONFIGS = {
    "default": {
        "height": 200,
        "width": "full",
    },
}

CKEDITOR_UPLOAD_PATH = "uploads/"

USE_DJANGO_JQUERY = True

CELERY_BROKER_URL = os.getenv("CELERY_BROKER_URL")
CELERY_RESULT_BACKEND = os.getenv("CELERY_BROKER_URL")


AVIA_URL = os.getenv("AVIA_URL")
AVIALOGIN = os.getenv("AVIALOGIN")
AVIAPASS = os.getenv("AVIAPASS")

ONESIGNAL_APPID = os.getenv("ONESIGNAL_APPID")
ONESIGNAL_RESTAPI = os.getenv("ONESIGNAL_RESTAPI")

NIKITA_LOGIN = os.getenv("NITKITA_LOGIN")
NIKITA_PASSWORD = os.getenv("NITKITA_PASSWORD")
NIKITA_SENDER = os.getenv("NITKITA_SENDER")

PAYLER_API_KEY = os.getenv("PAYLER_API_KEY")
