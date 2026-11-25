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

    def test_staff_receives_only_account_identifiers(self):
        self.client.force_authenticate(self.staff)
        profile = self.client.get(f"/api/usuarios/{self.owner.pk}/")
        self.assertEqual(set(profile.data), {"id", "username"})
        listing = self.client.get("/api/usuarios/")
        self.assertTrue(all(set(row) == {"id", "username"} for row in listing.data["results"]))

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
