"""Leitura para o worker interno. Este módulo não é exposto por HTTP."""

import base64
import json

from cryptography.hazmat.primitives.ciphers.aead import AESGCM

from ..models import Resposta
from .sealed_responses import response_context


def read_job_answers(*, owner_id, answer_ids, kms, allowed_key_ids):
    """O worker chama após autenticar a tarefa e validar o escopo do titular."""
    requested = set(answer_ids)
    rows = list(
        Resposta.objects.filter(usuario_id=owner_id, pk__in=requested)
        .order_by("pk")
        .values_list("pk", "pergunta_id", "resposta")
    )
    if len(rows) != len(requested):
        raise PermissionError("Uma ou mais respostas estão fora do escopo da tarefa.")

    answers = {}
    for answer_id, question_id, value in rows:
        envelope = json.loads(value)
        key_id = envelope["kid"]
        if envelope["v"] != 1 or key_id not in allowed_key_ids:
            raise ValueError("A chave ou o formato da resposta não é permitido para esta tarefa.")
        data_key = kms.decrypt(
            KeyId=key_id,
            CiphertextBlob=base64.b64decode(envelope["key"], validate=True),
            EncryptionAlgorithm="RSAES_OAEP_SHA_256",
        )["Plaintext"]
        plaintext = AESGCM(data_key).decrypt(
            base64.b64decode(envelope["nonce"], validate=True),
            base64.b64decode(envelope["data"], validate=True),
            response_context(key_id, answer_id, owner_id, question_id),
        )
        answers[answer_id] = {"pergunta": question_id, "resposta": plaintext.decode("utf-8")}
    return answers
