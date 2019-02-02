"""
Django settings for colossus project.

Generated by 'django-admin startproject' using Django 1.9.6.

For more information on this file, see
https://docs.djangoproject.com/en/1.9/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.9/ref/settings/

Created on May 16, 2016

@author: Jafar Taghiyar (jtaghiyar@bccrc.ca)

Updated Oct 19, 2017 by Spencer Vatrt-Watts (github.com/Spenca)
"""

import os
import sys

# Version
VERSION = "1.0.0"

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.9/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get('COLOSSUS_SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = bool(os.environ.get('COLOSSUS_DEBUG', False))

ALLOWED_HOSTS = os.environ.get('COLOSSUS_ALLOWED_HOSTS', '127.0.0.1').split()


# Application definition

INSTALLED_APPS = [
    'core.apps.CoreConfig',
    'account.apps.AccountConfig',
    'sisyphus.apps.SisyphusConfig',
    'dlp.apps.DlpConfig',
    'pbal.apps.PbalConfig',
    'tenx.apps.TenxConfig',
    'rest_framework',
    'django_filters', #filtering for rest_framework
    'django_extensions',
    'taggit',
    'simple_history',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'drf_yasg',
    # 'mod_wsgi.server',
]

MIDDLEWARE_CLASSES = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'simple_history.middleware.HistoryRequestMiddleware',
]

ROOT_URLCONF = 'colossus.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
                 os.path.join(BASE_DIR, 'templates')],
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


# Database
# https://docs.djangoproject.com/en/1.9/ref/settings/#databases

DATABASES = {
    'default': {
        # for older django versions use ".postgresql_psycopg2"
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('COLOSSUS_POSTGRESQL_NAME'),
        'USER': os.environ.get('COLOSSUS_POSTGRESQL_USER'),
        'PASSWORD': os.environ.get('COLOSSUS_POSTGRESQL_PASSWORD'),
        'HOST': os.environ.get('TANTALUS_POSTGRESQL_HOST', 'localhost'),
        'PORT': '5432',
    }
}


# Password validation
# https://docs.djangoproject.com/en/1.9/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/1.9/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'US/Pacific'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.9/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = os.environ.get(
    'COLOSSUS_STATIC_ROOT',
    os.path.join(BASE_DIR, 'static/'),)

# Media files
MEDIA_URL = "/media/"
MEDIA_ROOT = os.environ.get(
    'COLOSSUS_MEDIA_ROOT',
    os.path.join(BASE_DIR, 'media/'),)

# Login url
LOGIN_URL = '/account/login/'

# Enabled security settings
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_BROWSER_XSS_FILTER = True
X_FRAME_OPTIONS = "DENY"

# Rest Framework Settings
REST_FRAMEWORK = {
    # pagination setting
    'PAGE_SIZE': 10,
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'DEFAULT_FILTER_BACKENDS': ('django_filters.rest_framework.DjangoFilterBackend',),

}
