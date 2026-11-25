from itertools import batched

from django.db import migrations

from apps.diagnosis.legacy_encryption import EncryptedResponseField, response_cipher


def encrypt_existing_answers(apps, schema_editor):
    with schema_editor.connection.cursor() as cursor:
        cursor.execute("LOCK TABLE respostas IN SHARE ROW EXCLUSIVE MODE")
    answers = apps.get_model("api", "Resposta").objects.using(schema_editor.connection.alias)
    if not answers.exists():
        return
    cipher = response_cipher()
    values = answers.only("id", "resposta").order_by("id").iterator(chunk_size=500)
    for batch in batched(values, 500):
        for answer in batch:
            answer.resposta = cipher.encrypt(answer.resposta.encode("utf-8")).decode("ascii")
        answers.bulk_update(batch, ["resposta"], batch_size=500)


class Migration(migrations.Migration):
    dependencies = [("api", "0002_privacy_controls")]

    operations = [
        migrations.RunPython(encrypt_existing_answers),
        migrations.AlterField(
            model_name="resposta",
            name="resposta",
            field=EncryptedResponseField(),
        ),
    ]
