"""Cifra respostas com a chave pública do KMS, sem credencial de decifragem."""

import base64
import json
import os
from functools import lru_cache

from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding, rsa
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.db import models


class SealedResponse(str):
    """Conteúdo opaco já armazenado no banco."""


@lru_cache(maxsize=4)
def _public_key(encoded):
    try:
        key = serialization.load_der_public_key(base64.b64decode(encoded, validate=True))
    except (TypeError, ValueError) as error:
        raise ImproperlyConfigured("Configure uma chave pública RSA em formato DER base64.") from error
    if not isinstance(key, rsa.RSAPublicKey) or key.key_size < 2048:
        raise ImproperlyConfigured("A chave pública das respostas deve ser RSA de pelo menos 2048 bits.")
    return key


def encryption_config():
    key_id = settings.RESPONSE_KMS_KEY_ID
    if not key_id:
        raise ImproperlyConfigured("Configure DJANGO_RESPONSE_KMS_KEY_ID.")
    if settings.PUBLIC_DEPLOYMENT:
        arn = key_id.split(":")
        if len(arn) != 6 or arn[0] != "arn" or arn[2] != "kms" or not arn[5].startswith("key/"):
            raise ImproperlyConfigured("Use o ARN da chave KMS em DJANGO_RESPONSE_KMS_KEY_ID.")
    return key_id, _public_key(settings.RESPONSE_PUBLIC_KEY)


def response_context(key_id, answer_id, owner_id, question_id):
    return json.dumps(
        [1, key_id, str(answer_id), str(owner_id), str(question_id)], separators=(",", ":")
    ).encode("utf-8")


def seal_response(value, *, answer_id, owner_id, question_id):
    key_id, public_key = encryption_config()
    data_key = AESGCM.generate_key(bit_length=256)
    nonce = os.urandom(12)
    context = response_context(key_id, answer_id, owner_id, question_id)
    ciphertext = AESGCM(data_key).encrypt(nonce, value.encode("utf-8"), context)
    wrapped_key = public_key.encrypt(
        data_key,
        padding.OAEP(mgf=padding.MGF1(hashes.SHA256()), algorithm=hashes.SHA256(), label=None),
    )
    envelope = {"v": 1, "kid": key_id}
    for name, data in (("nonce", nonce), ("key", wrapped_key), ("data", ciphertext)):
        envelope[name] = base64.b64encode(data).decode("ascii")
    return SealedResponse(json.dumps(envelope, separators=(",", ":")))


class SealedResponseField(models.TextField):
    def get_prep_value(self, value):
        if value is None or isinstance(value, SealedResponse):
            return value
        raise ValueError("O banco só pode receber respostas cifradas.")

    def from_db_value(self, value, expression, connection):
        return SealedResponse(value) if value is not None else None
