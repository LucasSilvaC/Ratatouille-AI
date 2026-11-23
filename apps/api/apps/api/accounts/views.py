"""Atende cadastro, perfil, troca de senha e recuperação por e-mail."""

from django.contrib.auth import get_user_model
from django.contrib.auth.forms import PasswordResetForm
from django.contrib.auth.views import PasswordResetConfirmView
from django.urls import reverse_lazy
from rest_framework import generics, permissions, status, throttling
from rest_framework.response import Response

from ..mixins import ProtectedDeleteMixin
from ..pagination import CatalogPagination
from .forms import ConfirmarSenhaForm
from .passwords import definir_senha
from .serializers import (
    RegistroUsuarioSerializer,
    SolicitarRedefinicaoSenhaSerializer,
    TrocarSenhaSerializer,
    UsuarioSerializer,
)


class CriarUsuarioAPIView(generics.CreateAPIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = RegistroUsuarioSerializer


class UsuarioListView(generics.ListAPIView):
    permission_classes = [permissions.IsAdminUser]
    serializer_class = UsuarioSerializer
    pagination_class = CatalogPagination

    def get_queryset(self):
        return get_user_model().objects.order_by("pk")


class UsuarioDetailView(ProtectedDeleteMixin, generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = UsuarioSerializer

    def get_queryset(self):
        accounts = get_user_model().objects.all()
        user = self.request.user
        # Staff lê outros perfis. Alterações e exclusão ficam restritas ao titular.
        if user.is_staff and self.request.method in permissions.SAFE_METHODS:
            return accounts
        return accounts.filter(pk=user.pk)


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
        formulario = PasswordResetForm(serializer.validated_data)
        if formulario.is_valid():
            formulario.save(
                request=request,
                use_https=request.is_secure(),
                subject_template_name="api/redefinir_senha_assunto.txt",
                email_template_name="api/redefinir_senha_email.txt",
            )
        # A resposta é a mesma para endereços cadastrados e desconhecidos.
        return Response(
            {"detail": "Se houver uma conta elegível, enviaremos um link por e-mail."},
            status=status.HTTP_202_ACCEPTED,
        )


class ConfirmarRedefinicaoSenhaView(PasswordResetConfirmView):
    form_class = ConfirmarSenhaForm
    template_name = "api/redefinir_senha_confirmar.html"
    success_url = reverse_lazy("api:redefinir-senha-concluida")
