"""
Django settings for drf project.

Generated by 'django-admin startproject' using Django 1.10.5.

For more information on this file, see
https://docs.djangoproject.com/en/1.10/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.10/ref/settings/
"""

import os
from drf import config

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

ALLOWED_HOSTS = [config.get('ALLOWED_IP_ADDRESSES')]

# E-Mail
EMAIL_BACKEND = 'djcelery_email.backends.CeleryEmailBackend'
EMAIL_USE_TLS = True
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_HOST_USER = config.get('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = config.get('EMAIL_HOST_PASS')
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER

# Celery-RabbitMQ
CELERY_BROKER_URL = config.get('CELERY_BROKER_URL')


# Application definition

AUTH_USER_MODEL = 'core.DonkeyUser'

REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': (
       # 'rest_framework.permissions.IsAuthenticated',
    ),
    'DEFAULT_AUTHENTICATION_CLASSES': (
        #'rest_framework.authentication.BasicAuthentication',
        #'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.TokenAuthentication',
    )
}

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # Celery library
    'djcelery',
    'djcelery_email',
    # Restframework library
    'rest_framework',
    'rest_framework.authtoken',
    # Tree-Comment library
    'treebeard',
    # apps
    'mapi.apps.MApiConfig',
    'core.apps.CoreConfig',
    'batch.apps.BatchConfig',
]

MIDDLEWARE = [
    'django.middleware.cache.UpdateCacheMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.cache.FetchFromCacheMiddleware',
]

ROOT_URLCONF = 'drf.urls'


WSGI_APPLICATION = 'drf.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.10/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': config.get_db('DATABASE_NAME'),
        'USER': config.get_db('DATABASE_USER'),
        'PASSWORD': config.get_db('DATABASE_PASS'),
    }
}

# Password validation
# https://docs.djangoproject.com/en/1.10/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/1.10/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Asia/Seoul'

USE_I18N = True

USE_L10N = True

USE_TZ = True

'''
from django.utils import timezone
timezone.now()
datetime.datetime(2017, 4, 6, 2, 18, 4, 570044, tzinfo=<UTC>)
timezone.localtime(timezone.now())
datetime.datetime(2017, 4, 6, 11, 19, 19, 672131, tzinfo=<DstTzInfo 'Asia/Seoul' KST+9:00:00 STD>)
'''


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.10/howto/static-files/

STATIC_URL = '/static/'
