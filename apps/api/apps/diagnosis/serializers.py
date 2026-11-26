"""Valida perguntas e respostas e define os campos devolvidos em JSON."""

from rest_framework import serializers

from ..models import Pergunta, Resposta


class PerguntaSerializer(serializers.ModelSerializer):
    opcoes = serializers.ListField(
        child=serializers.CharField(max_length=120), max_length=20, required=False
    )

    class Meta:
        model = Pergunta
        fields = ("id", "pergunta", "opcoes", "aceita_texto_livre")

    def validate(self, attrs):
        opcoes = attrs.get("opcoes", getattr(self.instance, "opcoes", []))
        texto_livre = attrs.get(
            "aceita_texto_livre", getattr(self.instance, "aceita_texto_livre", False)
        )
        if bool(opcoes) == texto_livre:
            raise serializers.ValidationError(
                "Defina opções de resposta ou habilite explicitamente o texto livre."
            )
        if len(set(opcoes)) != len(opcoes):
            raise serializers.ValidationError({"opcoes": "As opções devem ser distintas."})
        return attrs


class RespostaSerializer(serializers.ModelSerializer):
    resposta = serializers.CharField(max_length=500, write_only=True)

    class Meta:
        model = Resposta
        fields = ("id", "resposta", "usuario", "pergunta")
        read_only_fields = ("usuario",)

    def validate(self, attrs):
        pergunta = attrs.get("pergunta", getattr(self.instance, "pergunta", None))
        if "resposta" not in attrs:
            if "pergunta" in attrs and pergunta.pk != self.instance.pergunta_id:
                raise serializers.ValidationError({"resposta": "Envie uma resposta para a nova pergunta."})
            return attrs
        resposta = attrs["resposta"]
        if pergunta is not None and not pergunta.aceita_texto_livre and resposta not in pergunta.opcoes:
            raise serializers.ValidationError({"resposta": "Selecione uma das opções da pergunta."})
        return attrs
