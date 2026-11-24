"""Publica as operações HTTP de classes, alimentos, nutrientes e medições."""

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView

from .serializers import (
    AlimentoNutrienteSerializer,
    AlimentoSerializer,
    ClasseSerializer,
    NutrienteSerializer,
)
from ..models import Alimento, AlimentoNutriente, Classe, Nutriente
from ..mixins import ProtectedDeleteMixin
from ..pagination import CatalogPagination
from ..permissions import StaffWritePermission
from .filters import AlimentoFilter, AlimentoNutrienteFilter


class CatalogListCreateView(ListCreateAPIView):
    permission_classes = (StaffWritePermission,)
    pagination_class = CatalogPagination


class CatalogDetailView(ProtectedDeleteMixin, RetrieveUpdateDestroyAPIView):
    permission_classes = (StaffWritePermission,)


class ClasseListCreateView(CatalogListCreateView):
    queryset = Classe.objects.order_by("pk")
    serializer_class = ClasseSerializer
    filter_backends = (SearchFilter,)
    search_fields = ("nome",)


class ClasseDetailView(CatalogDetailView):
    queryset = Classe.objects.all()
    serializer_class = ClasseSerializer


class AlimentoListCreateView(CatalogListCreateView):
    queryset = Alimento.objects.order_by("pk")
    serializer_class = AlimentoSerializer
    filter_backends = (DjangoFilterBackend, SearchFilter)
    filterset_class = AlimentoFilter
    search_fields = ("codigo", "descricao", "classe__nome")


class AlimentoDetailView(CatalogDetailView):
    queryset = Alimento.objects.all()
    serializer_class = AlimentoSerializer


class NutrienteListCreateView(CatalogListCreateView):
    queryset = Nutriente.objects.order_by("pk")
    serializer_class = NutrienteSerializer
    filter_backends = (DjangoFilterBackend, SearchFilter)
    filterset_fields = ("unidade",)
    search_fields = ("componente",)


class NutrienteDetailView(CatalogDetailView):
    queryset = Nutriente.objects.all()
    serializer_class = NutrienteSerializer


class AlimentoNutrienteListCreateView(CatalogListCreateView):
    queryset = AlimentoNutriente.objects.order_by("pk")
    serializer_class = AlimentoNutrienteSerializer
    filterset_class = AlimentoNutrienteFilter


class AlimentoNutrienteDetailView(CatalogDetailView):
    queryset = AlimentoNutriente.objects.all()
    serializer_class = AlimentoNutrienteSerializer
