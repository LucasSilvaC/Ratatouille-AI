from django.db import migrations

from apps.diagnosis.legacy_encryption import response_cipher
from apps.diagnosis.sealed_responses import SealedResponseField, seal_response


def seal_existing_answers(apps, schema_editor):
    with schema_editor.connection.cursor() as cursor:
        cursor.execute("LOCK TABLE respostas IN SHARE ROW EXCLUSIVE MODE")
        last_id = ""
        while True:
            cursor.execute(
                "SELECT id, usuario_id, pergunta_id, resposta "
                "FROM respostas WHERE id > %s ORDER BY id LIMIT 500",
                [last_id],
            )
            rows = cursor.fetchall()
            if not rows:
                return
            cipher = response_cipher()
            updates = [
                (
                    seal_response(
                        cipher.decrypt(value.encode("ascii")).decode("utf-8"),
                        answer_id=answer_id, owner_id=owner_id, question_id=question_id,
                    ),
                    answer_id,
                )
                for answer_id, owner_id, question_id, value in rows
            ]
            cursor.executemany("UPDATE respostas SET resposta = %s WHERE id = %s", updates)
            last_id = rows[-1][0]


class Migration(migrations.Migration):
    dependencies = [("api", "0003_encrypt_responses")]

    operations = [
        migrations.RunPython(seal_existing_answers),
        migrations.AlterField(model_name="resposta", name="resposta", field=SealedResponseField()),
    ]
