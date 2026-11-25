"""Aplica a política de contas confirmadas aos JWTs do piloto."""

from django.conf import settings
from drf_spectacular.contrib.rest_framework_simplejwt import SimpleJWTScheme
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.authentication import JWTAuthentication, default_user_authentication_rule


def conta_pode_autenticar(user):
    return default_user_authentication_rule(user) and (
        not settings.PUBLIC_DEPLOYMENT
        or bool(user.email_confirmado and user.email_confirmado == user.email)
    )


class PilotJWTAuthentication(JWTAuthentication):
    def get_user(self, validated_token):
        user = super().get_user(validated_token)
        if not conta_pode_autenticar(user):
            raise AuthenticationFailed("Conta indisponível.", code="account_unavailable")
        return user


class PilotJWTScheme(SimpleJWTScheme):
    target_class = PilotJWTAuthentication
