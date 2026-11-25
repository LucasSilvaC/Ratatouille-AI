"""Carrega o catálogo inicial em uma base já migrada."""

from django.core.management import BaseCommand, call_command
from django.db import connection, transaction

from ...models import Alimento, AlimentoNutriente, Classe, Nutriente


class Command(BaseCommand):
    help = "Carrega o fixture do catálogo se todas as tabelas do catálogo estiverem vazias."
    requires_migrations_checks = True

    @transaction.atomic
    def handle(self, *args, **options):
        # Permite leituras, mas impede outra carga ou escrita entre a checagem e o seed.
        with connection.cursor() as cursor:
            cursor.execute(
                "LOCK TABLE classes, alimento, nutriente, alimento_nutrientes "
                "IN SHARE ROW EXCLUSIVE MODE"
            )

        catalog_models = (Classe, Alimento, Nutriente, AlimentoNutriente)
        if any(model.objects.exists() for model in catalog_models):
            self.stdout.write("Catálogo existente preservado.")
            return

        call_command("loaddata", "seed.json", stdout=self.stdout, verbosity=options["verbosity"])
