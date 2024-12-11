"""
Django settings for studentsFeedback project.

Generated by 'django-manage startproject' using Django 5.1.3.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/5.1/ref/settings/
"""
import os
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-qq)u5ot8do$*((dtqfy0fmpe37m)0$ax#g!o5xda$95x(l=9v&'
ENCRYPTION_KEY = 'HPfw6Tsve7-d9j9zAyirgHRGC1sATzBVMneYgf_9I3I='

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

ALLOWED_HOSTS = ["*"]


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'manage',
    'core',
    'auto_moderation',
    'complaints'
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'studentsFeedback.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates']
        ,
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'studentsFeedback.wsgi.application'


# Database
# https://docs.djangoproject.com/en/5.1/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


# Password validation
# https://docs.djangoproject.com/en/5.1/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/5.1/topics/i18n/

LANGUAGE_CODE = 'ru'

TIME_ZONE = 'Europe/Moscow'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.1/howto/static-files/

STATIC_URL = 'static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')


LOGOUT_REDIRECT_URL = ''
# Default primary key field type
# https://docs.djangoproject.com/en/5.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

CELERY_BROKER_URL = 'redis://localhost:6379/'
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_BACKEND = 'redis://localhost:6379/'

CELERY_BROKER_CONNECTION_RETRY_ON_STARTUP = True



EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.yandex.ru'
EMAIL_PORT = 465
EMAIL_USE_TLS = False
EMAIL_USE_SSL = True
EMAIL_HOST_USER = 'AbuBandit1112@yandex.ru'
EMAIL_HOST_PASSWORD = 'lkmvlfzmkrpbxxkx'
DEFAULT_FROM_EMAIL = 'AbuBandit1112@yandex.ru'

URL = 'http://95.164.3.6'

MODERATION_REQUEST_URL = f'{URL}/moderation/auto-check/'
COMPLAINTS_VIEW_URL = f'{URL}/complaints/'
VIEW_COMPLAINTS_URL = f'{URL}/complaints/my/'

LOGIN_URL = '/admin/login/'

LOGOUT_REDIRECT_URL = '/'

#лимит на загрузку обращение за 1 запрос
COMPLAINTS_LIST_SIZE = 15

#Максимальное количество обращений за 5 минут -> далее спам
MAX_COMPLAINTS_COUNT = 3

#Время блокировки за спам (в минутах)
BAN_FOR_SPAM_TIME = 60

#Время блокировки за нецензурную лексику (в часах) (forever - навсегда)
BAN_MATS_TIME = 24*7