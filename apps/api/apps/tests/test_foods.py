from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase


class CatalogAPITests(APITestCase):
    def setUp(self):
        self.staff = get_user_model().objects.create_user(username="equipe", is_staff=True)
        self.client.force_authenticate(self.staff)

    def criar_classe(self):
        return self.client.post("/api/classes/", {"nome": "Frutas"}, format="json").data

    def criar_alimento(self, classe):
        return self.client.post(
            "/api/alimentos/",
            {"codigo": "F00001", "descricao": "Banana", "classe": classe["id"]},
            format="json",
        ).data

    def criar_nutriente(self):
        return self.client.post(
            "/api/nutrientes/", {"componente": "Fibra", "unidade": "g"}, format="json"
        ).data

    def test_equipe_gerencia_classes(self):
        collection = "/api/classes/"
        created = self.client.post(collection, {"nome": "Frutas"}, format="json")
        self.assertEqual(created.status_code, status.HTTP_201_CREATED)
        detail = f"{collection}{created.data['id']}/"
        self.assertEqual(self.client.get(collection).data["results"], [created.data])
        self.assertEqual(self.client.get(detail).data, created.data)
        updated = self.client.patch(detail, {"nome": "Frutas frescas"}, format="json")
        self.assertEqual(updated.data["nome"], "Frutas frescas")
        self.assertEqual(self.client.delete(detail).status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(self.client.get(detail).status_code, status.HTTP_404_NOT_FOUND)

    def test_aceita_codigo_de_seis_caracteres_com_barra_no_detalhe(self):
        classe = self.criar_classe()
        criado = self.client.post(
            "/api/alimentos/",
            {"codigo": "F/0001", "descricao": "Banana", "classe": classe["id"]},
            format="json",
        )

        self.assertEqual(criado.status_code, status.HTTP_201_CREATED)
        detalhe = self.client.get("/api/alimentos/F/0001/")
        self.assertEqual(detalhe.status_code, status.HTTP_200_OK)
        self.assertEqual(detalhe.data, criado.data)

    def test_equipe_gerencia_alimentos_com_codigo_textual(self):
        classe = self.criar_classe()
        collection = "/api/alimentos/"
        created = self.client.post(
            collection,
            {"codigo": "F00001", "descricao": "Banana", "classe": classe["id"]},
            format="json",
        )
        self.assertEqual(created.status_code, status.HTTP_201_CREATED)
        detail = f"{collection}F00001/"
        self.assertEqual(self.client.get(collection).data["results"], [created.data])
        self.assertEqual(self.client.get(detail).data, created.data)
        updated = self.client.put(
            detail, {"descricao": "Banana madura", "classe": classe["id"]}, format="json"
        )
        self.assertEqual(updated.status_code, status.HTTP_200_OK)
        self.assertEqual(updated.data["descricao"], "Banana madura")
        self.assertEqual(updated.data["codigo"], "F00001")
        self.assertEqual(self.client.delete(detail).status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(self.client.get(detail).status_code, status.HTTP_404_NOT_FOUND)

    def test_alteracao_do_codigo_do_alimento_e_rejeitada(self):
        classe = self.criar_classe()
        collection = "/api/alimentos/"
        self.criar_alimento(classe)
        detail = f"{collection}F00001/"

        response = self.client.patch(detail, {"codigo": "F00002"}, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("codigo", response.json()["fields"])
        self.assertEqual(self.client.get(collection).data["count"], 1)
        self.assertEqual(self.client.get(detail).data["codigo"], "F00001")

    def test_equipe_gerencia_nutrientes_sem_duplicar_componente_e_unidade(self):
        collection = "/api/nutrientes/"
        body = {"componente": "Fibra", "unidade": "g"}
        created = self.client.post(collection, body, format="json")
        self.assertEqual(created.status_code, status.HTTP_201_CREATED)
        duplicate = self.client.post(collection, body, format="json")
        self.assertEqual(duplicate.status_code, status.HTTP_400_BAD_REQUEST)
        detail = f"{collection}{created.data['id']}/"
        self.assertEqual(self.client.get(collection).data["results"], [created.data])
        self.assertEqual(self.client.get(detail).data, created.data)
        updated = self.client.patch(detail, {"unidade": "mg"}, format="json")
        self.assertEqual(updated.data["unidade"], "mg")
        self.assertEqual(self.client.delete(detail).status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(self.client.get(detail).status_code, status.HTTP_404_NOT_FOUND)

    def test_equipe_gerencia_medicoes_distintas_do_mesmo_par(self):
        alimento = self.criar_alimento(self.criar_classe())
        nutriente = self.criar_nutriente()
        collection = "/api/alimentos-nutrientes/"
        pair = {"alimento": alimento["codigo"], "nutriente": nutriente["id"]}
        first = self.client.post(collection, {**pair, "valor_numerico": 1.25}, format="json")
        self.assertEqual(first.status_code, status.HTTP_201_CREATED)
        second = self.client.post(collection, {**pair, "valor_numerico": None}, format="json")
        self.assertEqual(second.status_code, status.HTTP_201_CREATED)
        self.assertNotEqual(first.data["id"], second.data["id"])
        self.assertEqual(first.data["valor_numerico"], 1.25)
        self.assertIsNone(second.data["valor_numerico"])
        self.assertEqual(self.client.get(collection).data["results"], [first.data, second.data])
        detail = f"{collection}{first.data['id']}/"
        self.assertEqual(self.client.get(detail).data, first.data)
        updated = self.client.patch(detail, {"valor_numerico": 2.5}, format="json")
        self.assertEqual(updated.data["valor_numerico"], 2.5)
        self.assertEqual(self.client.delete(detail).status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(self.client.get(detail).status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(self.client.get(collection).data["results"], [second.data])

    def test_medicao_rejeita_valor_nao_finito(self):
        alimento = self.criar_alimento(self.criar_classe())
        nutriente = self.criar_nutriente()

        response = self.client.post(
            "/api/alimentos-nutrientes/",
            {"alimento": alimento["codigo"], "nutriente": nutriente["id"], "valor_numerico": "NaN"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("valor_numerico", response.json()["fields"])

    def test_remocao_de_registros_referenciados_e_rejeitada(self):
        classe = self.criar_classe()
        alimento = self.criar_alimento(classe)
        nutriente = self.criar_nutriente()
        measurement = self.client.post(
            "/api/alimentos-nutrientes/",
            {"alimento": alimento["codigo"], "nutriente": nutriente["id"]},
            format="json",
        ).data
        for url in (
            f"/api/classes/{classe['id']}/",
            f"/api/alimentos/{alimento['codigo']}/",
            f"/api/nutrientes/{nutriente['id']}/",
        ):
            with self.subTest(url=url):
                self.assertEqual(self.client.delete(url).status_code, status.HTTP_409_CONFLICT)
                self.assertEqual(self.client.get(url).status_code, status.HTTP_200_OK)
        self.assertEqual(
            self.client.get(f"/api/alimentos-nutrientes/{measurement['id']}/").data,
            measurement,
        )

    def test_usuario_autenticado_le_catalogo_e_somente_equipe_escreve(self):
        classe = self.criar_classe()
        url = "/api/classes/"
        self.client.force_authenticate(user=None)
        self.assertEqual(self.client.get(url).status_code, status.HTTP_401_UNAUTHORIZED)

        reader = get_user_model().objects.create_user(username="leitor")
        self.client.force_authenticate(reader)
        self.assertEqual(self.client.get(url).data["results"], [classe])
        self.assertEqual(
            self.client.post(url, {"nome": "Tubérculos"}, format="json").status_code,
            status.HTTP_403_FORBIDDEN,
        )
        self.assertEqual(
            self.client.delete(f"{url}{classe['id']}/").status_code,
            status.HTTP_403_FORBIDDEN,
        )

    def test_alimento_rejeita_codigo_de_tamanho_incorreto_e_classe_inexistente(self):
        data = {"codigo": "F00001", "descricao": "Banana", "classe": self.criar_classe()["id"]}
        for fields, error_field in (
            ({"codigo": "ABCDE"}, "codigo"),
            ({"codigo": "ABCDEFG"}, "codigo"),
            ({"classe": data["classe"] + 1}, "classe"),
        ):
            with self.subTest(fields=fields):
                response = self.client.post("/api/alimentos/", {**data, **fields}, format="json")
                self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
                self.assertIn(error_field, response.json()["fields"])
