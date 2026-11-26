"""Configuração do servidor Django, das migrações e dos testes."""

from datetime import timedelta
from os import environ
from pathlib import Path

from django.core.exceptions import ImproperlyConfigured, ValidationError
from django.core.management.utils import get_random_secret_key
from django.core.validators import DomainNameValidator

BASE_DIR = Path(__file__).resolve().parent.parent

PUBLIC_DEPLOYMENT = environ.get('DJANGO_PUBLIC_DEPLOYMENT', 'false').lower() == 'true'

# Uma chave estável mantém sessões, JWTs e links de recuperação válidos após reiniciar.
SECRET_KEY = environ.get('DJANGO_SECRET_KEY', '')
if PUBLIC_DEPLOYMENT and (
    len(SECRET_KEY) < 50 or len(set(SECRET_KEY)) < 5 or SECRET_KEY.startswith('django-insecure-')
):
    raise ImproperlyConfigured('Configure uma DJANGO_SECRET_KEY forte e estável para o modo público.')

SECRET_KEY = SECRET_KEY or get_random_secret_key()
DEBUG = not PUBLIC_DEPLOYMENT
ALLOWED_HOSTS = environ.get('DJANGO_ALLOWED_HOSTS', '').lower().split()

if PUBLIC_DEPLOYMENT:
    validate_host = DomainNameValidator()
    try:
        if not ALLOWED_HOSTS or any(
            not host.isascii() or host.endswith(('.', '.localhost')) for host in ALLOWED_HOSTS
        ):
            raise ValidationError('Missing or invalid domain.')
        for host in ALLOWED_HOSTS:
            validate_host(host)
    except ValidationError:
        raise ImproperlyConfigured(
            'Configure domínios explícitos em DJANGO_ALLOWED_HOSTS para o modo público.'
        ) from None

    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
    SECURE_SSL_REDIRECT = True
    SECURE_REDIRECT_EXEMPT = [r'^api/health/$']
    SECURE_HSTS_SECONDS = 31536000
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.db.DatabaseCache',
            'LOCATION': 'api_cache',
        }
    }

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
    'project.audit.RequestAuditMiddleware',
    'project.api_errors.ApiErrorMiddleware',
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
        'apps.accounts.authentication.PilotJWTAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': ('rest_framework.permissions.IsAuthenticated',),
    'EXCEPTION_HANDLER': 'project.api_errors.handle_api_exception',
    'DEFAULT_FILTER_BACKENDS': ['django_filters.rest_framework.DjangoFilterBackend'],
    'NUM_PROXIES': 1 if PUBLIC_DEPLOYMENT else 0,
    'DEFAULT_THROTTLE_RATES': {
        'login': '10/minute',
        'register': '5/minute',
        'token_refresh': '30/minute',
        'password_reset': '10/hour',
    },
}

SPECTACULAR_SETTINGS = {
    'TITLE': 'RatatouilleAI API',
    'VERSION': '1.0.0',
    'SERVE_INCLUDE_SCHEMA': False,
}

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=15),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=1),
    'AUTH_HEADER_TYPES': ('Bearer',),
    'CHECK_REVOKE_TOKEN': True,
    'USER_AUTHENTICATION_RULE': 'apps.accounts.authentication.conta_pode_autenticar',
}

PASSWORD_RESET_TIMEOUT = 3600
RESPONSE_KMS_KEY_ID = environ.get('DJANGO_RESPONSE_KMS_KEY_ID', '')
RESPONSE_PUBLIC_KEY = environ.get('DJANGO_RESPONSE_PUBLIC_KEY', '')
LEGACY_RESPONSE_ENCRYPTION_KEYS = environ.get('DJANGO_LEGACY_RESPONSE_ENCRYPTION_KEYS', '').split()
EMAIL_BACKEND = environ.get('DJANGO_EMAIL_BACKEND', 'django.core.mail.backends.smtp.EmailBackend')
if PUBLIC_DEPLOYMENT and EMAIL_BACKEND != 'django.core.mail.backends.smtp.EmailBackend':
    raise ImproperlyConfigured('Use o backend SMTP em DJANGO_EMAIL_BACKEND no modo público.')

EMAIL_HOST = environ.get('DJANGO_EMAIL_HOST', 'localhost')
EMAIL_PORT = int(environ.get('DJANGO_EMAIL_PORT', '587'))
EMAIL_HOST_USER = environ.get('DJANGO_EMAIL_HOST_USER', '')
EMAIL_HOST_PASSWORD = environ.get('DJANGO_EMAIL_HOST_PASSWORD', '')
EMAIL_USE_TLS = environ.get('DJANGO_EMAIL_USE_TLS', 'true').lower() == 'true'
if PUBLIC_DEPLOYMENT and not EMAIL_USE_TLS:
    raise ImproperlyConfigured('Ative DJANGO_EMAIL_USE_TLS no modo público.')

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

# O fixture contém o catálogo inicial. O esquema é gerenciado por migrate.
FIXTURE_DIRS = [BASE_DIR.parent.parent / "infra" / "database"]

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': environ.get('DJANGO_DB_NAME', 'ratatouille_api'),
        'USER': environ.get('DJANGO_DB_USER', 'ratatouille_api'),
        'PASSWORD': environ.get('DJANGO_DB_PASSWORD', 'ratatouille_api'),
        'HOST': environ.get('DJANGO_DB_HOST', '127.0.0.1'),
        'PORT': environ.get('DJANGO_DB_PORT', environ.get('POSTGRES_PORT', '5432')),
    }
}
if PUBLIC_DEPLOYMENT and DATABASES['default']['PASSWORD'].strip() in (
    '', 'ratatouille', 'ratatouille_api',
):
    raise ImproperlyConfigured(
        'Configure uma credencial própria em DJANGO_DB_PASSWORD para o modo público.'
    )

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
CORS_EXPOSE_HEADERS = ['X-Request-ID']

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {'safe': {'()': 'project.safe_logging.SafeLogFormatter'}},
    'handlers': {'safe': {'class': 'logging.StreamHandler', 'formatter': 'safe'}},
    'root': {'handlers': ['safe'], 'level': 'WARNING'},
    'loggers': {
        'api.audit': {'handlers': ['safe'], 'level': 'INFO', 'propagate': False},
        'django': {'handlers': ['safe'], 'level': 'WARNING', 'propagate': False},
        'django.request': {'handlers': ['safe'], 'level': 'WARNING', 'propagate': False},
        'django.server': {'handlers': ['safe'], 'level': 'WARNING', 'propagate': False},
        'gunicorn.error': {'handlers': ['safe'], 'level': 'ERROR', 'propagate': False},
        'gunicorn.access': {'handlers': [], 'propagate': False},
    },
}
