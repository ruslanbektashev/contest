import os

from .common_settings import *

SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY", "dev")

DEBUG = os.environ.get("DJANGO_DEBUG", "0") == "1"

ALLOWED_HOSTS = os.environ.get("DJANGO_ALLOWED_HOSTS", "").split(",")

SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
USE_X_FORWARDED_HOST = True
SECURE_SSL_REDIRECT = True

TIME_ZONE = 'Asia/Tashkent'

# Изменил разрешения для загрузки/скачивания файлов
FILE_UPLOAD_PERMISSIONS = 0o644

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.mysql",
        "NAME": os.environ["MYSQL_DATABASE"],
        "USER": os.environ["MYSQL_USER"],
        "PASSWORD": os.environ["MYSQL_PASSWORD"],
        "HOST": os.environ.get("DB_HOST", "db"),
        "PORT": os.environ.get("DB_PORT", "3306"),
        "OPTIONS": {
            "init_command": "SET sql_mode='STRICT_TRANS_TABLES'",
        },
    }
}

CELERY_RESULT_BACKEND = 'db+mysql://celery:H%5EyGr%3EhC%23pp5%28Msj@localhost/celery'

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'file': {
            'format': '[{asctime}] [{levelname}] {message}',
            'style': '{',
        },
    },
    'handlers': {
        'file': {
            'level': 'WARNING',
            'class': 'logging.FileHandler',
            'filename': '/app/django.log',
            'formatter': 'file',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file'],
            'level': 'WARNING',
            'propagate': True,
        },
    },
}
