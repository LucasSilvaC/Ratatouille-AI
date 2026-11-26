"""Adapta o formulário HTML de recuperação para usar a operação de senha da API."""

from django.contrib.auth.forms import PasswordResetForm, SetPasswordForm
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string

from .authentication import conta_pode_autenticar
from .passwords import definir_senha


class SolicitacaoRedefinicaoSenhaForm(PasswordResetForm):
    delivery_failed = False

    def get_users(self, email):
        return (user for user in super().get_users(email) if conta_pode_autenticar(user))

    def send_mail(
        self, subject_template_name, email_template_name, context, from_email,
        to_email, html_email_template_name=None,
    ):
        subject = "".join(render_to_string(subject_template_name, context).splitlines())
        body = render_to_string(email_template_name, context)
        message = EmailMultiAlternatives(subject, body, from_email, [to_email])
        if html_email_template_name:
            message.attach_alternative(render_to_string(html_email_template_name, context), "text/html")

        try:
            sent = message.send()
        except Exception:
            # Preserve a resposta pública mesmo se o backend falhar no envio.
            sent = 0
        if not sent:
            self.delivery_failed = True


class ConfirmarSenhaForm(SetPasswordForm):
    def save(self, commit=True):
        if commit:
            return definir_senha(self.user, self.cleaned_data["new_password1"])
        return super().save(commit=False)
