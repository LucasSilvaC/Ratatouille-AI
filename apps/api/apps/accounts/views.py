"""Atende cadastro, perfil, troca de senha e recuperação por e-mail."""

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.views import PasswordResetConfirmView
from django.db import transaction
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache
from rest_framework import generics, permissions, status, throttling
from rest_framework.response import Response
from rest_framework_simplejwt.token_blacklist.models import OutstandingToken
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from ..pagination import CatalogPagination
from .authentication import conta_pode_autenticar
from .forms import ConfirmarSenhaForm, SolicitacaoRedefinicaoSenhaForm
from .passwords import definir_senha
from .serializers import (
    IdentificacaoUsuarioSerializer,
    LoginTokenSerializer,
    RegistroUsuarioSerializer,
    SolicitarRedefinicaoSenhaSerializer,
    TrocarSenhaSerializer,
    UsuarioSerializer,
)


class PermiteCadastroLocal(permissions.BasePermission):
    message = "O cadastro do piloto é feito por convite."

    def has_permission(self, request, view):
        return not settings.PUBLIC_DEPLOYMENT


class CriarUsuarioAPIView(generics.CreateAPIView):
    authentication_classes = []
    permission_classes = [PermiteCadastroLocal]
    serializer_class = RegistroUsuarioSerializer
    throttle_classes = [throttling.ScopedRateThrottle]
    throttle_scope = "register"


class LoginAPIView(TokenObtainPairView):
    serializer_class = LoginTokenSerializer
    throttle_classes = [throttling.ScopedRateThrottle]
    throttle_scope = "login"


class RenovarTokenAPIView(TokenRefreshView):
    throttle_classes = [throttling.ScopedRateThrottle]
    throttle_scope = "token_refresh"


@method_decorator(never_cache, name="dispatch")
class UsuarioListView(generics.ListAPIView):
    permission_classes = [permissions.IsAdminUser]
    serializer_class = IdentificacaoUsuarioSerializer
    pagination_class = CatalogPagination

    def get_queryset(self):
        return get_user_model().objects.order_by("pk")


@method_decorator(never_cache, name="dispatch")
class UsuarioDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = UsuarioSerializer

    def get_queryset(self):
        accounts = get_user_model().objects.all()
        user = self.request.user
        # Staff identifica outras contas. Alterações e exclusão são do titular.
        if user.is_staff and self.request.method in permissions.SAFE_METHODS:
            return accounts
        return accounts.filter(pk=user.pk)

    def get_serializer_class(self):
        if self.request.user.is_staff and self.kwargs.get("pk") != self.request.user.pk:
            return IdentificacaoUsuarioSerializer
        return UsuarioSerializer

    @transaction.atomic
    def perform_destroy(self, instance):
        account = get_object_or_404(get_user_model().objects.select_for_update(), pk=instance.pk)
        OutstandingToken.objects.filter(user=account).delete()
        super().perform_destroy(account)


class TrocarSenhaAPIView(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = TrocarSenhaSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        definir_senha(request.user, serializer.validated_data["nova_senha"])
        return Response(status=status.HTTP_204_NO_CONTENT)


class ResetPasswordAPIView(generics.GenericAPIView):
    serializer_class = SolicitarRedefinicaoSenhaSerializer
    authentication_classes = []
    permission_classes = [permissions.AllowAny]
    throttle_classes = [throttling.ScopedRateThrottle]
    throttle_scope = "password_reset"

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        formulario = SolicitacaoRedefinicaoSenhaForm(serializer.validated_data)
        if formulario.is_valid():
            formulario.save(
                request=request,
                use_https=request.is_secure(),
                subject_template_name="api/redefinir_senha_assunto.txt",
                email_template_name="api/redefinir_senha_email.txt",
            )
        # A resposta é a mesma para endereços cadastrados e desconhecidos.
        response = Response(
            {"detail": "Se houver uma conta elegível, enviaremos um link por e-mail."},
            status=status.HTTP_202_ACCEPTED,
        )
        if formulario.delivery_failed:
            response.audit_failure_code = "smtp_send_failed"
        return response


class ConfirmarRedefinicaoSenhaView(PasswordResetConfirmView):
    form_class = ConfirmarSenhaForm
    template_name = "api/redefinir_senha_confirmar.html"
    success_url = reverse_lazy("api:redefinir-senha-concluida")

    def get_user(self, uidb64):
        user = super().get_user(uidb64)
        return user if conta_pode_autenticar(user) else None
