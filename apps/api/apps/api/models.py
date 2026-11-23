"""Define os modelos do ORM, suas tabelas, relações e restrições de integridade."""

from uuid import uuid4

from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinLengthValidator
from django.db import models
from django.db.models.functions import Length
from django.db.models.lookups import Exact


def novo_uuid():
    return str(uuid4())


class Classe(models.Model):
    id = models.AutoField(primary_key=True)
    nome = models.TextField(unique=True)

    class Meta:
        db_table = "classes"


class Alimento(models.Model):
    codigo = models.CharField(
        max_length=6, primary_key=True, validators=[MinLengthValidator(6)]
    )
    descricao = models.TextField()
    classe = models.ForeignKey(Classe, on_delete=models.PROTECT, db_index=False)

    class Meta:
        db_table = "alimento"
        indexes = [models.Index(fields=["classe"], name="idx_alimentos_classe")]
        constraints = [
            models.CheckConstraint(
                condition=Exact(Length("codigo"), 6), name="alimento_codigo_seis"
            )
        ]


class Nutriente(models.Model):
    id = models.AutoField(primary_key=True)
    componente = models.TextField()
    unidade = models.TextField()

    class Meta:
        db_table = "nutriente"
        unique_together = (("componente", "unidade"),)


class AlimentoNutriente(models.Model):
    # A tabela legada admite mais de uma linha para o mesmo par.
    id = models.AutoField(primary_key=True, db_column="rowid")
    alimento = models.ForeignKey(
        Alimento, on_delete=models.PROTECT, db_column="alimento_codigo", db_index=False
    )
    nutriente = models.ForeignKey(Nutriente, on_delete=models.PROTECT, db_index=False)
    valor_numerico = models.FloatField(null=True)

    class Meta:
        db_table = "alimento_nutrientes"
        indexes = [
            models.Index(fields=["alimento"], name="idx_an_alimento"),
            models.Index(
                fields=["nutriente", "valor_numerico"], name="idx_an_nutriente_valor"
            ),
        ]


class Pergunta(models.Model):
    id = models.TextField(primary_key=True, default=novo_uuid, editable=False)
    pergunta = models.TextField()

    class Meta:
        db_table = "perguntas"


class Resposta(models.Model):
    id = models.TextField(primary_key=True, default=novo_uuid, editable=False)
    resposta = models.TextField()
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, db_index=False)
    pergunta = models.ForeignKey(Pergunta, on_delete=models.PROTECT, db_index=False)

    class Meta:
        db_table = "respostas"
        indexes = [
            models.Index(fields=["usuario"], name="idx_respostas_usuario"),
            models.Index(fields=["pergunta"], name="idx_respostas_pergunta"),
        ]


class User(AbstractUser):
    id = models.AutoField(primary_key=True)
    nome = models.TextField(blank=True, default="")
    idade = models.IntegerField(null=True, blank=True)
    genero = models.TextField(null=True, blank=True)
    peso = models.FloatField(null=True, blank=True)
    altura = models.FloatField(null=True, blank=True)
    disposicao = models.FloatField(null=True, blank=True)

    class Meta:
        db_table = "auth_user"
        constraints = [
            models.CheckConstraint(condition=models.Q(idade__gte=0), name="usuario_idade_valida"),
            models.CheckConstraint(condition=models.Q(peso__gt=0), name="usuario_peso_valido"),
            models.CheckConstraint(condition=models.Q(altura__gt=0), name="usuario_altura_valida"),
        ]
