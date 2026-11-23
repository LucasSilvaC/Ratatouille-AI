"""Atualiza a senha e revoga os tokens de renovação em uma transação."""

from django.db import transaction
from django.utils import timezone
from rest_framework_simplejwt.token_blacklist.models import BlacklistedToken, OutstandingToken


@transaction.atomic
def definir_senha(user, raw_password):
    user.set_password(raw_password)
    user.save(update_fields=["password"])
    # O hash invalida JWTs de acesso. A lista de revogação bloqueia os de renovação.
    tokens = OutstandingToken.objects.filter(user=user, expires_at__gt=timezone.now())
    BlacklistedToken.objects.bulk_create(
        [BlacklistedToken(token_id=token_id) for token_id in tokens.values_list("pk", flat=True)],
        ignore_conflicts=True,
    )
    return user
