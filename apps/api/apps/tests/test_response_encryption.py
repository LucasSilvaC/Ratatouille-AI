import base64

from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding, rsa
from django.contrib.auth import get_user_model
from django.db import connection
from django.test import override_settings
from rest_framework.test import APITestCase

from ..diagnosis.agent_responses import read_job_answers
from ..models import Pergunta, Resposta


class ResponseEncryptionTests(APITestCase):
    def test_public_api_returns_metadata_only_even_to_the_owner(self):
        users = get_user_model().objects
        owner = users.create_user(username="titular")
        other = users.create_user(username="equipe", is_staff=True)
        question = Pergunta.objects.create(pergunta="Observação", aceita_texto_livre=True)
        answer = "informação fictícia"
        payload = {"pergunta": question.pk, "resposta": answer}
        self.client.force_authenticate(owner)

        first = self.client.post("/api/respostas/", payload)
        second = self.client.post("/api/respostas/", payload)
        self.assertEqual(first.status_code, 201)
        self.assertEqual(second.status_code, 201)
        self.assertNotIn("resposta", first.data)
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT resposta FROM respostas WHERE id IN (%s, %s)",
                [first.data["id"], second.data["id"]],
            )
            stored = [value for value, in cursor.fetchall()]
        self.assertEqual(len(stored), 2)
        self.assertNotEqual(stored[0], stored[1])
        self.assertTrue(all(answer not in value for value in stored))

        url = f"/api/respostas/{first.data['id']}/"
        self.assertNotIn("resposta", self.client.get(url).data)
        self.assertTrue(all("resposta" not in item for item in self.client.get(
            "/api/respostas/").data["results"]))
        self.assertNotIn("resposta", self.client.patch(url, {"resposta": "Atualizada"}).data)
        self.client.force_authenticate(other)
        self.assertEqual(self.client.get(url).status_code, 404)
        self.client.force_authenticate(None)
        self.assertEqual(self.client.get(url).status_code, 401)

    def test_worker_decrypts_only_requested_answers_of_the_authorized_owner(self):
        users = get_user_model().objects
        owner = users.create_user(username="titular")
        other = users.create_user(username="outro")
        question = Pergunta.objects.create(pergunta="Observação", aceita_texto_livre=True)
        key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
        public = key.public_key().public_bytes(
            serialization.Encoding.DER, serialization.PublicFormat.SubjectPublicKeyInfo
        )
        key_id = "test-key"
        with override_settings(
            RESPONSE_KMS_KEY_ID=key_id, RESPONSE_PUBLIC_KEY=base64.b64encode(public).decode()
        ):
            answer = Resposta.objects.create(usuario=owner, pergunta=question, resposta="Observação")

        class TestKms:
            calls = 0

            def decrypt(self, *, KeyId, CiphertextBlob, EncryptionAlgorithm):
                self.calls += 1
                if KeyId != key_id or EncryptionAlgorithm != "RSAES_OAEP_SHA_256":
                    raise AssertionError("Unexpected KMS key or algorithm")
                algorithm = padding.OAEP(
                    mgf=padding.MGF1(hashes.SHA256()), algorithm=hashes.SHA256(), label=None
                )
                return {"Plaintext": key.decrypt(CiphertextBlob, algorithm)}

        kms = TestKms()
        kwargs = {"answer_ids": [answer.pk], "kms": kms, "allowed_key_ids": {key_id}}
        with self.assertRaises(PermissionError):
            read_job_answers(owner_id=other.pk, **kwargs)
        self.assertEqual(kms.calls, 0)
        self.assertEqual(
            read_job_answers(owner_id=owner.pk, **kwargs),
            {answer.pk: {"pergunta": question.pk, "resposta": "Observação"}},
        )
