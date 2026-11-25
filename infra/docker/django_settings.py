"""Django settings for the Compose API service."""

from project.settings import *

DEBUG = False
ALLOWED_HOSTS = [*ALLOWED_HOSTS, '127.0.0.1']
FIXTURE_DIRS = [BASE_DIR / 'fixtures']
STATIC_ROOT = BASE_DIR / 'staticfiles'
MIDDLEWARE.insert(1, 'whitenoise.middleware.WhiteNoiseMiddleware')
