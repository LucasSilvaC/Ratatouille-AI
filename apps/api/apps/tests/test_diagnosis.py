from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from ..models import Pergunta, Resposta


class QuestionnaireApiTests(APITestCase):
    def setUp(self):
        users = get_user_model().objects
        self.user = users.create_user(username="participante")
        self.staff = users.create_user(username="equipe", is_staff=True)
        self.question = Pergunta.objects.create(
            pergunta="Qual é a sua fruta favorita?", opcoes=["Banana", "Manga"]
        )

    def test_only_authenticated_users_can_read_questions(self):
        url = reverse("api:pergunta-list")

        self.assertEqual(self.client.get(url).status_code, status.HTTP_401_UNAUTHORIZED)
        self.client.force_authenticate(self.user)

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["results"], [{
            "id": self.question.pk,
            "pergunta": "Qual é a sua fruta favorita?",
            "opcoes": ["Banana", "Manga"],
            "aceita_texto_livre": False,
        }])

    def test_staff_can_manage_questions(self):
        collection = reverse("api:pergunta-list")
        self.client.force_authenticate(self.user)
        payload = {
            "pergunta": "Você tem restrições alimentares?", "opcoes": ["Sim", "Não"]
        }
        self.assertEqual(
            self.client.post(collection, payload).status_code,
            status.HTTP_403_FORBIDDEN,
        )
        self.client.force_authenticate(self.staff)

        created = self.client.post(collection, payload)

        self.assertEqual(created.status_code, status.HTTP_201_CREATED)
        detail = reverse("api:pergunta-detail", args=[created.data["id"]])
        self.assertEqual(self.client.get(detail).data, created.data)
        updated = self.client.patch(detail, {"pergunta": "Quais alimentos você evita?"})
        self.assertEqual(updated.status_code, status.HTTP_200_OK)
        self.assertEqual(updated.data["pergunta"], "Quais alimentos você evita?")
        self.assertEqual(self.client.delete(detail).status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(self.client.get(detail).status_code, status.HTTP_404_NOT_FOUND)

    def test_staff_cannot_read_change_or_delete_another_users_answer(self):
        answer = Resposta.objects.create(pergunta=self.question, usuario=self.user, resposta="Banana")
        collection = reverse("api:resposta-list")
        detail = reverse("api:resposta-detail", args=[answer.pk])
        self.assertEqual(self.client.get(collection).status_code, status.HTTP_401_UNAUTHORIZED)
        self.client.force_authenticate(self.staff)

        self.assertEqual(self.client.get(collection).data["results"], [])
        self.assertEqual(self.client.get(detail).status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(
            self.client.patch(detail, {"resposta": "Manga"}).status_code,
            status.HTTP_404_NOT_FOUND,
        )
        self.assertEqual(self.client.delete(detail).status_code, status.HTTP_404_NOT_FOUND)
        self.client.force_authenticate(self.user)
        self.assertEqual(self.client.get(detail).status_code, status.HTTP_200_OK)
        self.assertNotIn("resposta", self.client.get(detail).data)

    def test_cannot_submit_answer_to_nonexistent_question(self):
        collection = reverse("api:resposta-list")
        self.client.force_authenticate(self.user)

        response = self.client.post(collection, {
            "resposta": "Banana",
            "pergunta": "7cd42cbd-b3d3-4ab0-9db8-1596a44d48e2",
        })

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("pergunta", response.data)
        self.assertEqual(self.client.get(collection).data["results"], [])

    def test_staff_cannot_delete_question_with_answers(self):
        Resposta.objects.create(pergunta=self.question, usuario=self.user, resposta="Banana")
        detail = reverse("api:pergunta-detail", args=[self.question.pk])
        self.client.force_authenticate(self.staff)

        response = self.client.delete(detail)

        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)
        self.assertEqual(self.client.get(detail).status_code, status.HTTP_200_OK)

    def test_owner_can_manage_own_answers(self):
        collection = reverse("api:resposta-list")
        self.client.force_authenticate(self.user)

        created = self.client.post(collection, {
            "resposta": "Banana",
            "pergunta": self.question.pk,
            "usuario": self.staff.pk,
        })

        self.assertEqual(created.status_code, status.HTTP_201_CREATED)
        self.assertEqual(created.data["usuario"], self.user.pk)
        detail = reverse("api:resposta-detail", args=[created.data["id"]])
        self.assertEqual(self.client.get(detail).data, created.data)
        self.assertEqual(self.client.get(collection).data["results"], [created.data])
        updated = self.client.patch(detail, {"resposta": "Manga", "usuario": self.staff.pk})
        self.assertEqual(updated.status_code, status.HTTP_200_OK)
        self.assertNotIn("resposta", updated.data)
        self.assertEqual(updated.data["usuario"], self.user.pk)
        self.assertEqual(self.client.delete(detail).status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(self.client.get(detail).status_code, status.HTTP_404_NOT_FOUND)
