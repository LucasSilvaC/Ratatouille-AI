"""Valida dados de conta e define quais campos entram e saem pela API."""

from collections.abc import Mapping

from django.contrib.auth import get_user_model, password_validation
from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import serializers


def validar_senha(password, user, field):
    try:
        password_validation.validate_password(password, user)
    except DjangoValidationError as error:
        raise serializers.ValidationError({field: error.messages}) from error


class IdentificacaoUsuarioSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = ("id", "username")


class UsuarioSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = (
            "id", "username", "email", "nome", "idade", "genero", "peso", "altura", "disposicao",
        )
        read_only_fields = ("email",)
        extra_kwargs = {"idade": {"min_value": 0}}

    def to_internal_value(self, data):
        # Normaliza o nome de usuário antes da validação de unicidade.
        if isinstance(data, Mapping) and isinstance(data.get("username"), str):
            data = data.copy()
            data["username"] = self.Meta.model.normalize_username(data["username"])
        return super().to_internal_value(data)

    def validate_peso(self, value):
        if value is not None and value <= 0:
            raise serializers.ValidationError("O peso deve ser maior que zero.")
        return value

    def validate_altura(self, value):
        if value is not None and value <= 0:
            raise serializers.ValidationError("A altura deve ser maior que zero.")
        return value

    def update(self, instance, validated_data):
        # Gravar só os campos enviados preserva uma troca de senha concorrente.
        for field, value in validated_data.items():
            setattr(instance, field, value)
        instance.save(update_fields=validated_data.keys())
        return instance


class RegistroUsuarioSerializer(UsuarioSerializer):
    email = serializers.EmailField(max_length=254)
    password = serializers.CharField(write_only=True, trim_whitespace=False)

    class Meta(UsuarioSerializer.Meta):
        fields = UsuarioSerializer.Meta.fields + ("password",)

    def validate(self, attrs):
        user = self.Meta.model(**{key: value for key, value in attrs.items() if key != "password"})
        validar_senha(attrs["password"], user, "password")
        return attrs

    def create(self, validated_data):
        return self.Meta.model.objects.create_user(**validated_data)


class TrocarSenhaSerializer(serializers.Serializer):
    senha_atual = serializers.CharField(write_only=True, trim_whitespace=False)
    nova_senha = serializers.CharField(write_only=True, trim_whitespace=False)

    def validate(self, attrs):
        user = self.context["request"].user
        if not user.check_password(attrs["senha_atual"]):
            raise serializers.ValidationError({"senha_atual": "A senha atual está incorreta."})
        validar_senha(attrs["nova_senha"], user, "nova_senha")
        return attrs


class SolicitarRedefinicaoSenhaSerializer(serializers.Serializer):
    email = serializers.EmailField(max_length=254)
