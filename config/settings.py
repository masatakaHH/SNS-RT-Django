#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals
from decouple import config
import os

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.2/howto/deployment/checklist/
ENVIRONMENT = os.environ.get('ENVIRONMENT', default='local')
# SECURITY WARNING: keep the secret key used in production secret!

# SECURITY WARNING: don't run with debug turned on in production!
if ENVIRONMENT == 'production':
    SECRET_KEY = os.environ.get('SECRET_KEY')
else:
    SECRET_KEY = config('SECRET_KEY')

ALLOWED_HOSTS = ["*"]


# Application definition
LOCAL_APPS = [
    'core',
    'accounts',
    'dashboard',    
]
DJANGO_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',    
    'django.contrib.humanize',
]
THIRD_PARTY_APPS = [        
    'escapejson',
    'corsheaders',
    'crispy_forms',    
    'django_jsonfield_backport',    
    'django_humanize',
    
]
INSTALLED_APPS = LOCAL_APPS + DJANGO_APPS + THIRD_PARTY_APPS

MIDDLEWARE = [    
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',    
]

# Authorization
AUTH_USER_MODEL = 'accounts.User'

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
            'libraries' : {
                'staticfiles': 'django.templatetags.static',                
                'notification_template': 'dashboard.templatetags.notification_template',                
                'sys_template': 'dashboard.templatetags.sys_template'
            }
            
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'
#ASGI_APPLICATION = 'config.asgi.application'
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

CRISPY_TEMPLATE_PACK = 'bootstrap4'
SITE_ID = 1

AUTHENTICATION_BACKENDS = [
    'config.backends.AuthBackend'    
]

# Internationalization
# https://docs.djangoproject.com/en/2.2/topics/i18n/

LANGUAGE_CODE = 'ja'

TIME_ZONE = 'Asia/Tokyo'

USE_I18N = True

USE_L10N = True

USE_TZ = True

DATA_UPLOAD_MAX_NUMBER_FIELDS=1024000

STATIC_ROOT = os.path.join(BASE_DIR, 'static/')

os.environ["DJANGO_ALLOW_ASYNC_UNSAFE"] = "true"

LOGIN_REDIRECT_URL = '/'

#EMAIL_BACKEND = "sendgrid_backend.SendgridBackend"
EMAIL_FILE_PATH = 'email_log'
EMAIL_HOST = 'smtp.sendgrid.net'
EMAIL_PORT = 587
EMAIL_FROM = "mycantest777@gmail.com"
NAME_FROM = "Hello"
EMAIL_USE_TLS = True

DATA_UPLOAD_MAX_MEMORY_SIZE = 1024000000
USE_THOUSAND_SEPARATOR = True

if ENVIRONMENT == 'local':
    # Static files (CSS, JavaScript, Images)
    # https://docs.djangoproject.com/en/2.2/howto/static-files/
    STATIC_URL = '/static/'
    STATIC_ROOT = os.path.join(BASE_DIR, 'static/')
    STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static_in_env/')]

    MEDIA_URL = "/media/"
    MEDIA_ROOT = os.path.join(BASE_DIR, 'media/')

    BACKEND_URL="http://127.0.0.1:8000"
    HOST_NAME = 'http://127.0.0.1:8000'
    FRONT_END_URL = "http://127.0.0.1:8000"
    
    PRODUCTION = False
    DEBUG = True
    ALLOWED_HOSTS = ['*', 'localhost','127.0.0.1']
    
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
        }
    }    
    
    SENDGRID_API_KEY=config('SENDGRID_API_KEY')
    BEARER_TOKEN = config('BEARER_TOKEN')
    API_KEY = config('TWITTER_API_KEY')
    API_SECRET = config('TWITTER_API_SECRET')
    client_id = config('TWITTER_CLIENT_ID')
    client_secret = config('TWITTER_CLIENT_SECRET')
    oauth_callback_url = config('TWITTER_OAUTH_CALLBACK_URL')
    
    STRIPE_SECRET_KEY = config('STRIPE_TEST_SECRET_KEY')
    STRIPE_PUBLIC_KEY = config('STRIPE_TEST_PUBLIC_KEY')
    STRIPE_ENDPOINT_SECRET = config('STRIPE_ENDPOINT_SECRET')
    STRIPE_PRICE_ID = config('STRIPE_PRICE_ID')

if ENVIRONMENT == 'production':
    PRODUCTION = True
    DEBUG = True
    ALLOWED_HOSTS = ['*']

    AUTH_PASSWORD_VALIDATORS = [
        {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
        {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
        {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
        {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'}
    ]

    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.mysql',
            'NAME': os.environ.get('RDS_DB_NAME'),
            'USER': os.environ.get('RDS_USERNAME'),
            'PASSWORD': os.environ.get('RDS_PASSWORD'),
            'HOST': os.environ.get('RDS_HOSTNAME'),
            'PORT': os.environ.get('RDS_PORT', default=3306),
            'OPTIONS': {
                'charset': 'utf8mb4'  # This is the important line
            }
        }
    }

    if "AWS_ACCESS_KEY_ID" in os.environ and "AWS_STORAGE_BUCKET_NAME" in os.environ:
        AWS_ACCESS_KEY_ID = os.environ["AWS_ACCESS_KEY_ID"]
        AWS_SECRET_ACCESS_KEY = os.environ["AWS_SECRET_ACCESS_KEY"]
        AWS_STORAGE_BUCKET_NAME = os.environ["AWS_STORAGE_BUCKET_NAME"]
        AWS_DEFAULT_ACL = None
        AWS_QUERYSTRING_AUTH = False
        AWS_S3_SIGNATURE_VERSION = 's3v4'
        AWS_S3_REGION_NAME = "ap-northeast-1"
        AWS_S3_ENCRYPTION = True
        AWS_S3_HOST = ''
        AWS_IS_GZIPPED = True
        AWS_S3_OBJECT_PARAMETERS = {
            'CacheControl': 'max-age=86400',
        }
        DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
        STATICFILES_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
        STATIC_URL = os.environ.get(
            'STATIC_URL', default=f'https://{AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com/')
        MEDIA_URL = os.environ.get(
            'MEDIA_URL', default=f'https://{AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com/')
        HOST_NAME = 'https://findmycampaign.com'
        BACKEND_URL="https://findmycampaign.com"
        FRONT_END_URL = "https://findmycampaign.com"
           
    
    SENDGRID_API_KEY=os.environ.get('SENDGRID_API_KEY')
    BEARER_TOKEN = os.environ['BEARER_TOKEN']
    API_KEY = os.environ['TWITTER_API_KEY']
    API_SECRET = os.environ['TWITTER_API_SECRET']
    client_id = os.environ['TWITTER_CLIENT_ID']
    client_secret = os.environ['TWITTER_CLIENT_SECRET']
    oauth_callback_url = os.environ['TWITTER_OAUTH_CALLBACK_URL']

    STRIPE_PUBLIC_KEY = os.environ['STRIPE_LIVE_PUBLIC_KEY']
    STRIPE_SECRET_KEY = os.environ['STRIPE_LIVE_SECRET_KEY']
    STRIPE_ENDPOINT_SECRET = os.environ['STRIPE_ENDPOINT_SECRET']
    STRIPE_PRICE_ID = os.environ['STRIPE_PRICE_ID']
    