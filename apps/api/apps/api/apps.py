"""Registra o app no Django e define o tipo padrão das chaves primárias."""

from django.apps import AppConfig


class ApiConfig(AppConfig):
    name = 'apps.api'
