# SECURITY WARNING: don't run with debug turned on in production!
from .base import *
from decouple import config, Csv

DEBUG = False

SECRET_KEY = config("SECRET_KEY")

ALLOWED_HOSTS = config('ALLOWED_HOSTS', cast=Csv())

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
