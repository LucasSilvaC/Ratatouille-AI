"""Valida entradas do catálogo e representa as relações pelo ID ou código."""

from rest_framework import serializers

from ..models import Alimento, AlimentoNutriente, Classe, Nutriente


class ClasseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Classe
        fields = ("id", "nome")


class AlimentoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Alimento
        fields = ("codigo", "descricao", "classe")
        extra_kwargs = {"codigo": {"trim_whitespace": False}}

    def get_fields(self):
        fields = super().get_fields()
        # Na atualização o código já está na URL e pode ser omitido no corpo.
        if self.instance is not None:
            fields["codigo"].required = False
        return fields

    def validate_codigo(self, value):
        if self.instance is not None and self.instance.codigo != value:
            raise serializers.ValidationError("O código de um alimento existente é imutável.")
        return value


class NutrienteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Nutriente
        fields = ("id", "componente", "unidade")


class AlimentoNutrienteSerializer(serializers.ModelSerializer):
    class Meta:
        model = AlimentoNutriente
        fields = ("id", "alimento", "nutriente", "valor_numerico")
