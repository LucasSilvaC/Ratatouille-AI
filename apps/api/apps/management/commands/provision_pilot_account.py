"""Cria a conta de um participante cujo endereço já foi confirmado pela equipe."""

from secrets import token_urlsafe

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.core.management import BaseCommand, CommandError
from django.db import IntegrityError, transaction


class Command(BaseCommand):
    help = "Provisiona uma conta do piloto. Confirme a posse do e-mail antes de executar."
    requires_migrations_checks = True

    def add_arguments(self, parser):
        parser.add_argument("--staff", action="store_true", help="Concede escrita no catálogo e nas perguntas.")

    def handle(self, *args, **options):
        user_model = get_user_model()
        try:
            username = user_model.normalize_username(input("Nome de usuário: ").strip())
            email = user_model.objects.normalize_email(input("E-mail confirmado: ").strip())
        except EOFError as error:
            raise CommandError("Informe o nome de usuário e o e-mail confirmado.") from error

        try:
            user_model._meta.get_field("username").clean(username, None)
            user_model._meta.get_field("email_confirmado").clean(email, None)
        except ValidationError as error:
            raise CommandError("Informe um nome de usuário e um e-mail válidos.") from error
        if not email:
            raise CommandError("Informe o e-mail confirmado.")

        try:
            with transaction.atomic():
                user = user_model.objects.create_user(
                    username=username,
                    email=email,
                    email_confirmado=email,
                    password=token_urlsafe(32),
                    is_staff=options["staff"],
                )
        except IntegrityError:
            raise CommandError("O nome de usuário ou o e-mail confirmado já está em uso.") from None

        self.stdout.write(f"Conta {user.pk} provisionada. O participante pode solicitar a definição de senha.")
