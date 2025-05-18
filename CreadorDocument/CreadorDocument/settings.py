"""
Django settings for CreadorDocument project.

Based on 'django-admin startproject' using Django 2.1.2.

For more information on this file, see
https://docs.djangoproject.com/en/2.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.1/ref/settings/
"""

import os
import posixpath
from pathlib import Path
import warnings
warnings.filterwarnings("default")

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '123d5433-eed1-4a00-9555-38a129d84b3a'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []

# Application references
# https://docs.djangoproject.com/en/2.1/ref/settings/#std:setting-INSTALLED_APPS
INSTALLED_APPS = [
    'app',
    'documentos',
    # Add your apps here to enable them
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'social_django',
]

# Middleware framework
# https://docs.djangoproject.com/en/2.1/topics/http/middleware/
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'CreadorDocument.urls'

# Template configuration
# https://docs.djangoproject.com/en/2.1/topics/templates/
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
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

WSGI_APPLICATION = 'CreadorDocument.wsgi.application'
# Database
# https://docs.djangoproject.com/en/2.1/ref/settings/#databases
'''
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}
'''
DATABASES = {
    'default': {
        'ENGINE': 'mssql',
        'NAME': 'gestionDocumentos',
        'USER': 'usuario',
        'PASSWORD': 'Koishikomeiji2',
        'HOST': 'localhost\\SQLEXPRESS',
        'PORT': '',  # usualmente se deja vacío si es el puerto por defecto
        'OPTIONS': {
            'driver': 'ODBC Driver 17 for SQL Server',
            #'unicode_results': True,
        },
    }
}

# Password validation
# https://docs.djangoproject.com/en/2.1/ref/settings/#auth-password-validators
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
# https://docs.djangoproject.com/en/2.1/topics/i18n/
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_L10N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.1/howto/static-files/
STATIC_URL = '/static/'
STATIC_ROOT = posixpath.join(*(BASE_DIR.split(os.path.sep) + ['static']))

BASE_DIR = Path(__file__).resolve().parent.parent

STATICFILES_DIRS = [
    BASE_DIR / 'CreadorDocument' / 'static',
]
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

AUTH_USER_MODEL = 'app.Usuario'
AUTHENTICATION_BACKENDS = [
    'app.backends.EmailOrUsernameModelBackend',  # usa tu app real aquí
    'django.contrib.auth.backends.ModelBackend',
]
GOOGLE_OAUTH2_URL = "https://accounts.google.com/o/oauth2/v2/auth?response_type=code&client_id=1019076673616-kcm22556hlpkkflrf9jflqq9hn77ehmv.apps.googleusercontent.com&redirect_uri=http://localhost:8000/oauth2callback/&scope=https://www.googleapis.com/auth/drive.file https://www.googleapis.com/auth/gmail.send&access_type=offline"

# Configuración para Google OAuth2
SOCIAL_AUTH_GOOGLE_OAUTH2_KEY = '1019076673616-kcm22556hlpkkflrf9jflqq9hn77ehmv.apps.googleusercontent.com'  # Tu Client ID
SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET = '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'  # Reemplázalo con tu Client Secret

'''SOCIAL_AUTH_GOOGLE_OAUTH2_SCOPE = [
    'https://www.googleapis.com/auth/drive.file',  # Acceso a Google Drive
    'https://www.googleapis.com/auth/gmail.send',  # Acceso para enviar correos
]'''

# URL de redirección (callback) después de la autenticación
SOCIAL_AUTH_GOOGLE_OAUTH2_REDIRECT_URI = 'http://localhost:8000/oauth2callback/'

# Configuración de autenticación backend (opcional si ya tienes configurado un modelo personalizado)
AUTHENTICATION_BACKENDS = (
    'social_core.backends.google.GoogleOAuth2',  # Asegúrate de usar este backend
    'django.contrib.auth.backends.ModelBackend',
)
CLIENT_SECRET_FILE = os.path.join(BASE_DIR, 'credentials', 'client_secret_1019076673616-kcm22556hlpkkflrf9jflqq9hn77ehmv.apps.googleusercontent.com.json')
CLIENT_ID = "1019076673616-kcm22556hlpkkflrf9jflqq9hn77ehmv.apps.googleusercontent.com"
GOOGLE_OAUTH_SCOPES = [
    "openid",
    "https://www.googleapis.com/auth/userinfo.email",
    "https://www.googleapis.com/auth/gmail.send",
    "https://www.googleapis.com/auth/drive.file",
]