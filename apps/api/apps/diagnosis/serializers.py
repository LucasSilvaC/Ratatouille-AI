"""Valida perguntas e respostas e define os campos devolvidos em JSON."""

from rest_framework import serializers

from ..models import Pergunta, Resposta


class PerguntaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Pergunta
        fields = ("id", "pergunta")


class RespostaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Resposta
        fields = ("id", "resposta", "usuario", "pergunta")
        read_only_fields = ("usuario",)
