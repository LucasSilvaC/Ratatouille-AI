"""Traduz parâmetros da URL em filtros do ORM nas listagens do catálogo."""

from django_filters import rest_framework as filters

from ..models import Alimento, AlimentoNutriente


class AlimentoFilter(filters.FilterSet):
    codigo = filters.CharFilter(strip=False, label="Código exato do alimento")
    descricao = filters.CharFilter(
        lookup_expr="icontains",
        label="Trecho da descrição, sem distinção entre maiúsculas e minúsculas",
    )

    class Meta:
        model = Alimento
        fields = ("codigo", "descricao", "classe")


class AlimentoNutrienteFilter(filters.FilterSet):
    alimento = filters.CharFilter(field_name="alimento_id", strip=False, label="Código do alimento")
    valor_min = filters.NumberFilter(field_name="valor_numerico", lookup_expr="gte")
    valor_max = filters.NumberFilter(field_name="valor_numerico", lookup_expr="lte")

    class Meta:
        model = AlimentoNutriente
        fields = ("alimento", "nutriente", "valor_min", "valor_max")
