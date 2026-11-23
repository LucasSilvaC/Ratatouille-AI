from urllib.parse import urlsplit

from django.contrib.auth import get_user_model
from django.core import mail
from django.test import override_settings
from rest_framework import status
from rest_framework.test import APITestCase


@override_settings(EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend")
class PasswordRecoveryTests(APITestCase):
    def test_recupera_senha_por_link_sem_revelar_contas(self):
        user = get_user_model().objects.create_user(
            username="teste", email="teste@example.com", password="Original-987!"
        )
        tokens = self.client.post(
            "/api/token/", {"username": user.username, "password": "Original-987!"}
        )
        self.assertEqual(tokens.status_code, status.HTTP_200_OK)
        solicitacao = self.client.post("/api/redefinir_senha/", {"email": user.email})
        inexistente = self.client.post("/api/redefinir_senha/", {"email": "outro@example.com"})
        self.assertEqual(solicitacao.status_code, status.HTTP_202_ACCEPTED)
        self.assertEqual(inexistente.status_code, status.HTTP_202_ACCEPTED)
        self.assertEqual(solicitacao.json(), inexistente.json())
        self.assertEqual(len(mail.outbox), 1)
        link = next(line for line in mail.outbox[0].body.splitlines() if line.startswith("http"))
        token_path = urlsplit(link).path
        confirmacao = self.client.get(token_path)
        self.assertEqual(confirmacao.status_code, status.HTTP_302_FOUND)
        resposta = self.client.post(
            confirmacao.url, {"new_password1": "Nova-443!Teste", "new_password2": "Nova-443!Teste"}
        )
        self.assertEqual(resposta.status_code, status.HTTP_302_FOUND)
        user.refresh_from_db()
        self.assertTrue(user.check_password("Nova-443!Teste"))
        refresh = self.client.post("/api/token/refresh/", {"refresh": tokens.json()["refresh"]})
        self.assertEqual(refresh.status_code, status.HTTP_401_UNAUTHORIZED)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {tokens.json()['access']}")
        self.assertEqual(self.client.get("/api/perguntas/").status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(self.client.get(token_path).status_code, status.HTTP_200_OK)
        self.assertContains(self.client.get(token_path), "Link inválido ou expirado")
