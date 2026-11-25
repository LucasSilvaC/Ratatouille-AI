from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from rest_framework.test import APITestCase
from rest_framework_simplejwt.token_blacklist.models import OutstandingToken
from rest_framework_simplejwt.tokens import RefreshToken

from ..models import Pergunta, Resposta


class PrivacyTests(APITestCase):
    def setUp(self):
        users = get_user_model()
        self.owner = users.objects.create_user(username="titular", peso=65)
        self.staff = users.objects.create_user(username="equipe", is_staff=True)
        self.question = Pergunta.objects.create(pergunta="Preferência")

    def test_private_profile_cannot_be_cached(self):
        token = RefreshToken.for_user(self.owner).access_token
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

        response = self.client.get(f"/api/usuarios/{self.owner.pk}/")

        self.assertEqual(response.status_code, 200)
        self.assertIn("no-store", response.headers.get("Cache-Control", ""))
        self.assertIn("private", response.headers["Cache-Control"])

    def test_answer_metadata_cannot_be_cached(self):
        answer = Resposta.objects.create(usuario=self.owner, pergunta=self.question, resposta="X")
        token = RefreshToken.for_user(self.owner).access_token
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

        for path in ("/api/respostas/", f"/api/respostas/{answer.pk}/"):
            with self.subTest(path=path):
                response = self.client.get(path)
                self.assertEqual(response.status_code, 200)
                self.assertIn("no-store", response.headers.get("Cache-Control", ""))
                self.assertIn("private", response.headers["Cache-Control"])

    def test_staff_receives_only_account_identifiers(self):
        self.client.force_authenticate(self.staff)
        profile = self.client.get(f"/api/usuarios/{self.owner.pk}/")
        self.assertEqual(set(profile.data), {"id", "username"})
        listing = self.client.get("/api/usuarios/")
        self.assertIn("no-store", listing.headers.get("Cache-Control", ""))
        self.assertTrue(all(set(row) == {"id", "username"} for row in listing.data["results"]))

    def test_jwt_access_to_another_accounts_data_respects_ownership(self):
        other = get_user_model().objects.create_user(username="outro")
        answer = Resposta.objects.create(usuario=self.owner, pergunta=self.question, resposta="X")
        profile_url = f"/api/usuarios/{self.owner.pk}/"
        answer_url = f"/api/respostas/{answer.pk}/"

        for account, profile_status in ((other, 404), (self.staff, 200)):
            with self.subTest(staff=account.is_staff):
                token = RefreshToken.for_user(account).access_token
                self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

                profile = self.client.get(profile_url)
                self.assertEqual(profile.status_code, profile_status)
                if account.is_staff:
                    self.assertEqual(set(profile.json()), {"id", "username"})

                listing = self.client.get("/api/respostas/", {"pergunta": self.question.pk})
                self.assertEqual(listing.status_code, 200)
                self.assertEqual(listing.json()["results"], [])
                self.assertEqual(self.client.get(answer_url).status_code, 404)
                for path in (profile_url, answer_url):
                    for method in (self.client.put, self.client.patch, self.client.delete):
                        self.assertEqual(method(path, {}, format="json").status_code, 404)

    def test_staff_with_django_permissions_cannot_open_local_user_admin(self):
        self.staff.user_permissions.add(
            Permission.objects.get(content_type__app_label="api", codename="view_user")
        )
        self.client.force_login(self.staff)
        self.assertEqual(self.client.get("/admin/api/user/").status_code, 403)

    def test_deleting_account_also_deletes_its_answers(self):
        answer = Resposta.objects.create(usuario=self.owner, pergunta=self.question, resposta="X")
        RefreshToken.for_user(self.owner)
        token_id = OutstandingToken.objects.get(user=self.owner).pk
        self.client.force_authenticate(self.owner)
        self.assertEqual(self.client.delete(f"/api/usuarios/{self.owner.pk}/").status_code, 204)
        self.assertFalse(Resposta.objects.filter(pk=answer.pk).exists())
        self.assertFalse(OutstandingToken.objects.filter(pk=token_id).exists())
        self.assertFalse(get_user_model().objects.filter(pk=self.owner.pk).exists())

    def test_question_requires_configured_format_before_accepting_an_answer(self):
        self.client.force_authenticate(self.owner)
        payload = {"pergunta": self.question.pk, "resposta": "Texto livre"}
        self.assertEqual(self.client.post("/api/respostas/", payload).status_code, 400)

    def test_structured_answers_allow_only_listed_options(self):
        self.question.opcoes = ["Sim", "Não"]
        self.question.save(update_fields=["opcoes"])
        self.client.force_authenticate(self.owner)
        url = "/api/respostas/"
        payload = {"pergunta": self.question.pk, "resposta": "Valor fora da lista"}
        self.assertEqual(self.client.post(url, payload).status_code, 400)
        self.assertEqual(self.client.post(url, {**payload, "resposta": "Sim"}).status_code, 201)

    def test_free_text_requires_explicit_opt_in_and_is_bounded(self):
        self.client.force_authenticate(self.staff)
        payload = {"pergunta": "Observação necessária"}
        self.assertEqual(self.client.post("/api/perguntas/", payload).status_code, 400)
        question = self.client.post("/api/perguntas/", {**payload, "aceita_texto_livre": True})
        self.assertEqual(question.status_code, 201)
        self.client.force_authenticate(self.owner)
        url = "/api/respostas/"
        payload = {"pergunta": question.data["id"], "resposta": "X" * 501}
        self.assertEqual(self.client.post(url, payload).status_code, 400)
        self.assertEqual(self.client.post(url, {**payload, "resposta": "Observação"}).status_code, 201)
