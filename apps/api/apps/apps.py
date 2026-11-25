"""Registra o app no Django e define o tipo padrão das chaves primárias."""

from django.apps import AppConfig
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured


class ApiConfig(AppConfig):
    name = 'apps'
    label = 'api'

    def ready(self):
        if settings.PUBLIC_DEPLOYMENT:
            from .diagnosis.sealed_responses import encryption_config

            if settings.LEGACY_RESPONSE_ENCRYPTION_KEYS:
                raise ImproperlyConfigured("A chave legada só pode ser usada na migração isolada.")
            encryption_config()
