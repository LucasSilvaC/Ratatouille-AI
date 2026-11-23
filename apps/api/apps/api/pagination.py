"""Define o tamanho padrão das páginas para as listagens da API."""

from rest_framework import pagination


class CatalogPagination(pagination.PageNumberPagination):
    page_size = 50
