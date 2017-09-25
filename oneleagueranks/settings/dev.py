from .base import *

DEBUG = True

# Database
# https://docs.djangoproject.com/en/1.9/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'oneleagueranks',
        'USER': 'postgres',
        'HOST': '127.0.0.1',
    },
}