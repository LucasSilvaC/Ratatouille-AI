from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase

from ..models import Alimento, AlimentoNutriente, Classe, Nutriente, Pergunta, Resposta


class ListFilterTests(APITestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(username="leitor")
        self.client.force_authenticate(self.user)

    def test_alimentos_combinam_codigo_descricao_e_classe(self):
        fruta = Classe.objects.create(nome="Frutas")
        vegetal = Classe.objects.create(nome="Vegetais")
        Alimento.objects.bulk_create([
            Alimento(codigo="F00001", descricao="Banana madura", classe=fruta),
            Alimento(codigo="F00002", descricao="Banana verde", classe=fruta),
            Alimento(codigo="V00001", descricao="Alface", classe=vegetal),
        ])
        for filtros, esperados in (
            ({"codigo": "F00002"}, ["F00002"]),
            ({"descricao": "BANANA"}, ["F00001", "F00002"]),
            ({"classe": vegetal.pk}, ["V00001"]),
            ({"descricao": "madura", "classe": vegetal.pk}, []),
            ({"search": "verde"}, ["F00002"]),
        ):
            with self.subTest(filtros=filtros):
                resposta = self.client.get("/api/alimentos/", filtros)
                self.assertEqual(resposta.status_code, status.HTTP_200_OK)
                self.assertEqual([item["codigo"] for item in resposta.data["results"]], esperados)

    def test_busca_catalogo_e_filtra_medicoes(self):
        fruta = Classe.objects.create(nome="Frutas")
        Classe.objects.create(nome="Vegetais")
        alimento = Alimento.objects.create(codigo="F00001", descricao="Banana", classe=fruta)
        fibra = Nutriente.objects.create(componente="Fibra alimentar", unidade="g")
        Nutriente.objects.create(componente="Vitamina A", unidade="mg")
        medicao = AlimentoNutriente.objects.create(
            alimento=alimento, nutriente=fibra, valor_numerico=2.5
        )
        AlimentoNutriente.objects.create(alimento=alimento, nutriente=fibra, valor_numerico=1.5)

        for rota, filtros, esperado in (
            ("classes", {"search": "frut"}, fruta.pk),
            ("nutrientes", {"search": "FIBRA", "unidade": "g"}, fibra.pk),
            (
                "alimentos-nutrientes",
                {"alimento": alimento.pk, "nutriente": fibra.pk, "valor_min": 2, "valor_max": 3},
                medicao.pk,
            ),
        ):
            with self.subTest(rota=rota):
                resposta = self.client.get(f"/api/{rota}/", filtros)
                self.assertEqual(resposta.status_code, status.HTTP_200_OK)
                self.assertEqual([item["id"] for item in resposta.data["results"]], [esperado])

    def test_busca_perguntas_e_filtra_respostas_sem_expor_outro_autor(self):
        pergunta = Pergunta.objects.create(pergunta="Qual sua fruta favorita?")
        outra = Pergunta.objects.create(pergunta="Qual sua altura?")
        outro_autor = get_user_model().objects.create_user(username="outro")
        esperada = Resposta.objects.create(pergunta=pergunta, usuario=self.user, resposta="Banana")
        Resposta.objects.create(pergunta=outra, usuario=self.user, resposta="Banana")
        Resposta.objects.create(pergunta=pergunta, usuario=outro_autor, resposta="Banana")
        outra_resposta_propria = Resposta.objects.create(
            pergunta=pergunta, usuario=self.user, resposta="Maçã"
        )

        perguntas = self.client.get("/api/perguntas/", {"search": "fruta"})
        self.assertEqual([item["id"] for item in perguntas.data["results"]], [pergunta.pk])
        respostas = self.client.get("/api/respostas/", {"pergunta": pergunta.pk})
        self.assertEqual(
            {item["id"] for item in respostas.data["results"]},
            {esperada.pk, outra_resposta_propria.pk},
        )
