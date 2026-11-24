"""Reúne regras de acesso HTTP compartilhadas entre domínios."""

from rest_framework import permissions


class StaffWritePermission(permissions.IsAuthenticated):
    def has_permission(self, request, view):
        return super().has_permission(request, view) and (
            request.method in permissions.SAFE_METHODS or request.user.is_staff
        )
