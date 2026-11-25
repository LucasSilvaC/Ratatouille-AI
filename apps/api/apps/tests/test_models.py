from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import DataError, IntegrityError, transaction
from django.test import TestCase

from ..models import Alimento, AlimentoNutriente, Classe, Nutriente, Pergunta, Resposta


class UsuarioTests(TestCase):
    def test_armazena_disposicao_fracionaria(self):
        usuario = get_user_model().objects.create_user(
            username="teste", nome="Teste", password="ficticia", disposicao=0.75
        )

        usuario.refresh_from_db()

        self.assertIsInstance(usuario.disposicao, float)
        self.assertEqual(usuario.disposicao, 0.75)
        self.assertTrue(usuario.check_password("ficticia"))


class AlimentoTests(TestCase):
    def test_codigo_precisa_ter_exatamente_seis_caracteres(self):
        classe = Classe.objects.create(nome="Frutas")
        for codigo, database_error in (("ABCDE", IntegrityError), ("ABCDEFG", DataError)):
            alimento = Alimento(codigo=codigo, descricao="Banana", classe=classe)
            with self.subTest(codigo=codigo):
                with self.assertRaises(ValidationError):
                    alimento.full_clean()
                with self.assertRaises(database_error), transaction.atomic():
                    alimento.save(force_insert=True)
        Alimento.objects.create(codigo="ABC123", descricao="Banana", classe=classe)


class AlimentoNutrienteTests(TestCase):
    def test_preserva_medicoes_do_mesmo_par_com_identidades_distintas(self):
        classe = Classe.objects.create(nome="Frutas")
        alimento = Alimento.objects.create(codigo="F00001", descricao="Banana", classe=classe)
        nutriente = Nutriente.objects.create(componente="Potássio", unidade="mg")

        primeira = AlimentoNutriente.objects.create(
            alimento=alimento, nutriente=nutriente, valor_numerico=350
        )
        segunda = AlimentoNutriente.objects.create(
            alimento=alimento, nutriente=nutriente, valor_numerico=360
        )

        self.assertNotEqual(primeira.pk, segunda.pk)
        self.assertEqual(
            AlimentoNutriente.objects.get(pk=primeira.pk).valor_numerico, 350
        )
        self.assertEqual(
            AlimentoNutriente.objects.get(pk=segunda.pk).valor_numerico, 360
        )


class DiagnosticoTests(TestCase):
    def test_banco_rejeita_identificador_fora_do_formato_uuid(self):
        usuario = get_user_model().objects.create_user(username="teste")
        pergunta = Pergunta.objects.create(pergunta="Pergunta")
        dados_resposta = {"pergunta": pergunta, "usuario": usuario, "resposta": "Resposta"}

        for model, fields in ((Pergunta, {"pergunta": "Pergunta"}), (Resposta, dados_resposta)):
            with self.subTest(model=model), self.assertRaises(IntegrityError), transaction.atomic():
                model.objects.create(id="invalido", **fields)
