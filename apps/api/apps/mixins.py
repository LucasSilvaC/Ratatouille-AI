"""Compartilha o tratamento de exclusões bloqueadas por vínculos entre tabelas."""

from django.db.models import ProtectedError
from rest_framework import exceptions, status


class ProtectedDeleteMixin:
    def perform_destroy(self, instance):
        try:
            super().perform_destroy(instance)
        except ProtectedError as error:
            raise ProtectedDeletion from error


class ProtectedDeletion(exceptions.APIException):
    status_code = status.HTTP_409_CONFLICT
    default_detail = "O registro possui v?nculos e n?o pode ser exclu?do."
    default_code = "protected"
