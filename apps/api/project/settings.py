"""Configuração do servidor Django, das migrações e dos testes."""

from datetime import timedelta
from os import environ
from pathlib import Path

from django.core.management.utils import get_random_secret_key

BASE_DIR = Path(__file__).resolve().parent.parent

# Uma chave estável mantém sessões, JWTs e links de recuperação válidos após reiniciar.
SECRET_KEY = environ.get('DJANGO_SECRET_KEY') or get_random_secret_key()

DEBUG = True

ALLOWED_HOSTS = environ.get('DJANGO_ALLOWED_HOSTS', '').split()

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework_simplejwt',
    'drf_spectacular',
    'rest_framework',
    'apps.apps.ApiConfig',
    'corsheaders',
    'rest_framework_simplejwt.token_blacklist',
    'django_filters',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'corsheaders.middleware.CorsMiddleware',
]

REST_FRAMEWORK = {
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_FILTER_BACKENDS': ['django_filters.rest_framework.DjangoFilterBackend'],
    'DEFAULT_THROTTLE_RATES': {'password_reset': '10/hour'},
}

SPECTACULAR_SETTINGS = {
    'TITLE': 'RatatouilleAI API',
    'VERSION': '1.0.0',
    'SERVE_INCLUDE_SCHEMA': False,
}

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=250),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=1),
    'AUTH_HEADER_TYPES': ('Bearer',),
    'CHECK_REVOKE_TOKEN': True,
}

PASSWORD_RESET_TIMEOUT = 3600
EMAIL_BACKEND = environ.get('DJANGO_EMAIL_BACKEND', 'django.core.mail.backends.smtp.EmailBackend')
EMAIL_HOST = environ.get('DJANGO_EMAIL_HOST', 'localhost')
EMAIL_PORT = int(environ.get('DJANGO_EMAIL_PORT', '587'))
EMAIL_HOST_USER = environ.get('DJANGO_EMAIL_HOST_USER', '')
EMAIL_HOST_PASSWORD = environ.get('DJANGO_EMAIL_HOST_PASSWORD', '')
EMAIL_USE_TLS = environ.get('DJANGO_EMAIL_USE_TLS', 'true').lower() == 'true'
EMAIL_TIMEOUT = 10
DEFAULT_FROM_EMAIL = environ.get('DJANGO_DEFAULT_FROM_EMAIL', 'webmaster@localhost')

ROOT_URLCONF = 'project.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'project.wsgi.application'

# A API usa o SQLite local. A cópia de distribuição fica em infra/database.
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite',
    }
}

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

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True

STATIC_URL = 'static/'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# O primeiro componente identifica o app que fornece o modelo de autenticação.
AUTH_USER_MODEL = 'api.User'

CORS_ALLOWED_ORIGINS = ['http://localhost:3000']
