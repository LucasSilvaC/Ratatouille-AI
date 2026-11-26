from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from ..accounts.serializers import UsuarioSerializer


VALID_PASSWORD = "amora-47-mural-azul!"


class RegistroTests(APITestCase):
    def test_registro_publico_armazena_hash_e_protege_atributos_de_acesso(self):
        response = self.client.post(
            "/api/register/",
            {
                "username": "pessoa",
                "email": "pessoa@example.test",
                "password": VALID_PASSWORD,
                "nome": "Pessoa",
                "is_staff": True,
                "is_superuser": True,
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertNotIn("password", response.data)
        self.assertNotIn("is_staff", response.data)
        account = get_user_model().objects.get(username="pessoa")
        self.assertTrue(account.check_password(VALID_PASSWORD))
        self.assertFalse(account.is_staff)
        self.assertFalse(account.is_superuser)

    def test_registro_exige_email_valido_e_senha_nativa(self):
        for payload, field in (
            ({"password": VALID_PASSWORD}, "email"),
            ({"email": "invalido", "password": VALID_PASSWORD}, "email"),
            ({"email": "teste@example.test", "password": "123"}, "password"),
        ):
            with self.subTest(payload=payload):
                response = self.client.post(
                    "/api/register/", {"username": "pessoa", **payload}, format="json"
                )
                self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
                self.assertIn(field, response.json()["fields"])
        self.assertFalse(get_user_model().objects.exists())

    def test_registro_valida_unicidade_do_username_normalizado(self):
        get_user_model().objects.create_user(username="Ångström")
        response = self.client.post(
            "/api/register/",
            {
                "username": "Ångström",
                "email": "pessoa@example.test",
                "password": VALID_PASSWORD,
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("username", response.json()["fields"])


class PerfilTests(APITestCase):
    def setUp(self):
        self.owner = get_user_model().objects.create_user(
            username="perfil", email="perfil@example.test"
        )
        self.staff = get_user_model().objects.create_user(username="operador", is_staff=True)
        self.other = get_user_model().objects.create_user(username="outro")
        self.url = f"/api/usuarios/{self.owner.pk}/"

    def test_acesso_ao_perfil_e_lista_respeitam_o_escopo(self):
        self.assertEqual(self.client.get(self.url).status_code, status.HTTP_401_UNAUTHORIZED)
        for account, expected in ((self.owner, 200), (self.staff, 200), (self.other, 404)):
            with self.subTest(account=account.username):
                self.client.force_authenticate(account)
                self.assertEqual(self.client.get(self.url).status_code, expected)
        self.assertEqual(self.client.get("/api/usuarios/").status_code, status.HTTP_403_FORBIDDEN)
        self.client.force_authenticate(self.staff)
        response = self.client.get("/api/usuarios/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 3)
        for profile in response.data["results"]:
            self.assertNotIn("password", profile)
            self.assertNotIn("is_staff", profile)

    def test_apenas_o_titular_altera_o_perfil_sem_trocar_email_de_recuperacao(self):
        self.client.force_authenticate(self.staff)
        response = self.client.patch(self.url, {"nome": "Alterado"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(self.client.delete(self.url).status_code, status.HTTP_404_NOT_FOUND)

        self.client.force_authenticate(self.owner)
        response = self.client.patch(
            self.url, {"nome": "Alterado", "email": "novo@example.test", "is_staff": True}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.owner.refresh_from_db()
        self.assertEqual(self.owner.nome, "Alterado")
        self.assertEqual(self.owner.email, "perfil@example.test")
        self.assertFalse(self.owner.is_staff)

    def test_rejeita_medidas_incompativeis_com_o_modelo(self):
        self.client.force_authenticate(self.owner)
        response = self.client.patch(
            self.url,
            {"idade": -1, "peso": 0, "altura": "Infinity", "disposicao": "NaN"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(set(response.json()["fields"]), {"idade", "peso", "altura", "disposicao"})

    def test_atualizacao_de_perfil_preserva_troca_de_senha_concorrente(self):
        serializer = UsuarioSerializer(self.owner, data={"nome": "Alterado"}, partial=True)
        serializer.is_valid(raise_exception=True)
        updated_account = get_user_model().objects.get(pk=self.owner.pk)
        updated_account.set_password(VALID_PASSWORD)
        updated_account.save(update_fields=["password"])

        serializer.save()

        self.owner.refresh_from_db()
        self.assertTrue(self.owner.check_password(VALID_PASSWORD))
        self.assertEqual(self.owner.nome, "Alterado")


class AutenticacaoTests(APITestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="pessoa", password=VALID_PASSWORD
        )

    def test_jwt_obtem_e_renova_token_para_acessar_o_proprio_perfil(self):
        response = self.client.post(
            reverse("api:token_obtain_pair"),
            {"username": self.user.username, "password": VALID_PASSWORD},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        refreshed = self.client.post(
            reverse("api:token_refresh"), {"refresh": response.data["refresh"]}, format="json"
        )
        self.assertEqual(refreshed.status_code, status.HTTP_200_OK)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {refreshed.data['access']}")
        profile = self.client.get(reverse("api:usuario-detail", args=[self.user.pk]))
        self.assertEqual(profile.status_code, status.HTTP_200_OK)
        self.assertEqual(profile.data["id"], self.user.pk)

    def test_troca_senha_exige_a_atual_e_revoga_tokens_ja_emitidos(self):
        tokens = self.client.post(
            reverse("api:token_obtain_pair"),
            {"username": self.user.username, "password": VALID_PASSWORD},
            format="json",
        ).data
        url = "/api/senha/"
        nova_senha = "orvalho-48-caneta!"
        self.assertEqual(self.client.post(url).status_code, status.HTTP_401_UNAUTHORIZED)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {tokens['access']}")
        invalid = self.client.post(
            url, {"senha_atual": "incorreta", "nova_senha": nova_senha}, format="json"
        )
        self.assertEqual(invalid.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("senha_atual", invalid.json()["fields"])
        weak = self.client.post(
            url, {"senha_atual": VALID_PASSWORD, "nova_senha": "123"}, format="json"
        )
        self.assertEqual(weak.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("password_too_short", weak.json()["fields"]["nova_senha"])

        response = self.client.post(
            url, {"senha_atual": VALID_PASSWORD, "nova_senha": nova_senha}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password(nova_senha))
        self.assertFalse(self.user.check_password(VALID_PASSWORD))
        profile = self.client.get(reverse("api:usuario-detail", args=[self.user.pk]))
        self.assertEqual(profile.status_code, status.HTTP_401_UNAUTHORIZED)
        refresh = self.client.post(
            reverse("api:token_refresh"), {"refresh": tokens["refresh"]}, format="json"
        )
        self.assertEqual(refresh.status_code, status.HTTP_401_UNAUTHORIZED)
