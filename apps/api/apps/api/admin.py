"""Configura a edição de contas e perfis alimentares no Django Admin."""

from django.contrib import admin

from django.contrib.auth.admin import UserAdmin

from .models import User


@admin.register(User)
class RatatouilleUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        ("Perfil alimentar", {"fields": ("nome", "idade", "genero", "peso", "altura", "disposicao")}),
    )
