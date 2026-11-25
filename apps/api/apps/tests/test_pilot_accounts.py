from io import StringIO
from unittest.mock import patch
from urllib.parse import urlsplit

from django.contrib.auth import get_user_model
from django.core import mail
from django.core.cache import cache
from django.core.management import CommandError, call_command
from django.test import SimpleTestCase, override_settings
from rest_framework.test import APIClient, APITestCase


class PilotRegistrationTests(SimpleTestCase):
    @override_settings(PUBLIC_DEPLOYMENT=True)
    def test_cadastro_publico_e_desabilitado_no_piloto(self):
        response = APIClient().post("/api/register/", {}, secure=True)

        self.assertEqual(response.status_code, 403)


@override_settings(PUBLIC_DEPLOYMENT=True, EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend")
class PilotPasswordRecoveryTests(APITestCase):
    def setUp(self):
        cache.clear()
        self.addCleanup(cache.clear)

    def test_recuperacao_ignora_conta_legada_sem_email_confirmado(self):
        user = get_user_model().objects.create_user(
            username="legado", email="legado@example.test", password="Original-987!"
        )

        response = self.client.post("/api/redefinir_senha/", {"email": user.email}, secure=True)
        unknown = self.client.post("/api/redefinir_senha/", {"email": "outro@example.test"}, secure=True)

        self.assertEqual(response.status_code, 202)
        self.assertEqual(response.json(), unknown.json())
        self.assertFalse(mail.outbox)

    def test_convite_permite_definir_senha_pelo_email_confirmado(self):
        email = "participante@example.test"
        output = StringIO()
        with patch("sys.stdin", StringIO(f"participante\n{email}\n")):
            call_command("provision_pilot_account", stdout=output)
        self.assertNotIn(email, output.getvalue())

        self.assertEqual(
            self.client.post("/api/redefinir_senha/", {"email": email}, secure=True).status_code,
            202,
        )
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to, [email])
        link = next(line for line in mail.outbox[0].body.splitlines() if line.startswith("https://"))
        redirect = self.client.get(urlsplit(link).path, secure=True)
        self.assertEqual(redirect.status_code, 302)
        confirm = self.client.post(
            redirect.url,
            {"new_password1": "Nova-443!Teste", "new_password2": "Nova-443!Teste"},
            secure=True,
        )
        self.assertEqual(confirm.status_code, 302)
        tokens = self.client.post(
            "/api/token/", {"username": "participante", "password": "Nova-443!Teste"}, secure=True
        )
        self.assertEqual(tokens.status_code, 200)

    def test_piloto_rejeita_login_e_tokens_de_conta_legada(self):
        user = get_user_model().objects.create_user(
            username="legado", email="legado@example.test", password="Original-987!"
        )
        credentials = {"username": user.username, "password": "Original-987!"}
        with override_settings(PUBLIC_DEPLOYMENT=False):
            local = self.client.post("/api/token/", credentials, secure=True)
        self.assertEqual(local.status_code, 200)

        self.assertEqual(self.client.post("/api/token/", credentials, secure=True).status_code, 401)
        refresh = self.client.post(
            "/api/token/refresh/", {"refresh": local.json()["refresh"]}, secure=True
        )
        self.assertEqual(refresh.status_code, 401)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {local.json()['access']}")
        self.assertEqual(self.client.get("/api/perguntas/", secure=True).status_code, 401)

    def test_provisionamento_rejeita_email_confirmado_duplicado_sem_diferenciar_maiusculas(self):
        with patch("sys.stdin", StringIO("primeiro\nConta@example.test\n")):
            call_command("provision_pilot_account", stdout=StringIO())
        with patch("sys.stdin", StringIO("segundo\nconta@example.test\n")):
            with self.assertRaisesRegex(CommandError, "já está em uso"):
                call_command("provision_pilot_account", stdout=StringIO())
