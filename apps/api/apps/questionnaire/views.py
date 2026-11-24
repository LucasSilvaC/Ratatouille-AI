"""Atende perguntas e limita cada resposta ao usuário que a criou."""

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


class RespostaListCreateView(RespostaOwnerMixin, generics.ListCreateAPIView):
    pagination_class = CatalogPagination
    filter_backends = (DjangoFilterBackend, SearchFilter)
    filterset_fields = ("pergunta",)
    search_fields = ("resposta",)

    def perform_create(self, serializer):
        # O autor vem da autenticação, independentemente do corpo da requisição.
        serializer.save(usuario=self.request.user)


class RespostaDetailView(RespostaOwnerMixin, generics.RetrieveUpdateDestroyAPIView):
    pass
