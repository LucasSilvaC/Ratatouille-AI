"""Atende perguntas e limita cada resposta ao usuário que a criou."""

from django.db import transaction
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics, permissions
from rest_framework.filters import SearchFilter

from ..models import Pergunta, Resposta
from .serializers import PerguntaSerializer, RespostaSerializer
from ..mixins import ProtectedDeleteMixin
from ..pagination import CatalogPagination
from ..permissions import StaffWritePermission


class PerguntaListCreateView(generics.ListCreateAPIView):
    queryset = Pergunta.objects.order_by("id")
    serializer_class = PerguntaSerializer
    permission_classes = (StaffWritePermission,)
    pagination_class = CatalogPagination
    filter_backends = (SearchFilter,)
    search_fields = ("pergunta",)


class PerguntaDetailView(ProtectedDeleteMixin, generics.RetrieveUpdateDestroyAPIView):
    queryset = Pergunta.objects.all()
    serializer_class = PerguntaSerializer
    permission_classes = (StaffWritePermission,)


class RespostaOwnerMixin:
    # O Swagger identifica o modelo pelo queryset vazio, sem consultar respostas.
    queryset = Resposta.objects.none()
    serializer_class = RespostaSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        # Lista e detalhe partem do escopo do autor antes de procurar registros.
        return Resposta.objects.filter(usuario=self.request.user).order_by("id")


@method_decorator(never_cache, name="dispatch")
class RespostaListCreateView(RespostaOwnerMixin, generics.ListCreateAPIView):
    pagination_class = CatalogPagination
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ("pergunta",)

    def perform_create(self, serializer):
        # O autor vem da autenticação, independentemente do corpo da requisição.
        serializer.save(usuario=self.request.user)


@method_decorator(never_cache, name="dispatch")
class RespostaDetailView(RespostaOwnerMixin, generics.RetrieveUpdateDestroyAPIView):
    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.select_for_update() if self.request.method in {"PUT", "PATCH"} else queryset

    @transaction.atomic
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)
