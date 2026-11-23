"""Adapta o formulário HTML de recuperação para usar a operação de senha da API."""

from django.contrib.auth.forms import SetPasswordForm

from .passwords import definir_senha


class ConfirmarSenhaForm(SetPasswordForm):
    def save(self, commit=True):
        if commit:
            return definir_senha(self.user, self.cleaned_data["new_password1"])
        return super().save(commit=False)
