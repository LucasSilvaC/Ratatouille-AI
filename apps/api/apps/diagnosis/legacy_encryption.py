"""Compatibilidade exclusiva com a migração histórica de respostas Fernet."""

from functools import lru_cache

from cryptography.fernet import Fernet, InvalidToken, MultiFernet
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.db import models


@lru_cache(maxsize=4)
def _cipher(keys):
    if not keys:
        raise ImproperlyConfigured("Configure DJANGO_LEGACY_RESPONSE_ENCRYPTION_KEYS para a migração.")
    try:
        return MultiFernet([Fernet(key) for key in keys])
    except (TypeError, ValueError) as error:
        raise ImproperlyConfigured(
            "DJANGO_LEGACY_RESPONSE_ENCRYPTION_KEYS contém uma chave Fernet inválida."
        ) from error


def response_cipher():
    return _cipher(tuple(settings.LEGACY_RESPONSE_ENCRYPTION_KEYS))


class EncryptedResponseField(models.TextField):
    def get_prep_value(self, value):
        value = super().get_prep_value(value)
        if value is None:
            return None
        return response_cipher().encrypt(value.encode("utf-8")).decode("ascii")

    def from_db_value(self, value, expression, connection):
        if value is None:
            return None
        try:
            return response_cipher().decrypt(value.encode("utf-8")).decode("utf-8")
        except (InvalidToken, UnicodeError):
            raise ValueError("Não foi possível decifrar o conteúdo da resposta.") from None
