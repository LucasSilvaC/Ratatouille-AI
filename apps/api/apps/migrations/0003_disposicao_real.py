from importlib import import_module
from math import isfinite

from django.db import migrations, models


USUARIO_TEXT = import_module(".0002_remodelar_catalogo_respostas", __package__).USUARIO
USUARIO_REAL = USUARIO_TEXT.replace("disposicao TEXT", "disposicao REAL")


def trocar_tabela(schema_editor, create_sql, expressao):
    schema_editor.execute(create_sql.replace("CREATE TABLE usuario ", "CREATE TABLE usuario_novo "))
    schema_editor.execute(
        "INSERT INTO usuario_novo (id, nome, idade, senha, genero, peso, altura, disposicao) "
        f"SELECT id, nome, idade, senha, genero, peso, altura, {expressao} FROM usuario"
    )
    schema_editor.execute("DROP TABLE usuario")
    schema_editor.execute("ALTER TABLE usuario_novo RENAME TO usuario")


def converter_para_real(apps, schema_editor):
    with schema_editor.connection.cursor() as cursor:
        cursor.execute("SELECT type FROM pragma_table_info('usuario') WHERE name = 'disposicao'")
        if cursor.fetchone() in (None, ("REAL",)):
            return
        cursor.execute("SELECT id, disposicao FROM usuario WHERE disposicao IS NOT NULL")
        valores = []
        for usuario_id, disposicao in cursor:
            try:
                numero = float(disposicao)
                if not isfinite(numero):
                    raise ValueError
            except (TypeError, ValueError, OverflowError) as error:
                raise RuntimeError("Corrija os valores não numéricos de usuario.disposicao.") from error
            valores.append((numero, usuario_id))

    trocar_tabela(schema_editor, USUARIO_REAL, "NULL")
    with schema_editor.connection.cursor() as cursor:
        cursor.executemany("UPDATE usuario SET disposicao = %s WHERE id = %s", valores)


def converter_para_texto(apps, schema_editor):
    trocar_tabela(schema_editor, USUARIO_TEXT, "CAST(disposicao AS TEXT)")


class Migration(migrations.Migration):
    dependencies = [("api", "0002_remodelar_catalogo_respostas")]

    operations = [
        migrations.SeparateDatabaseAndState(
            database_operations=[migrations.RunPython(converter_para_real, converter_para_texto)],
            state_operations=[
                migrations.AlterField(
                    model_name="usuario", name="disposicao", field=models.FloatField(null=True)
                ),
            ],
        ),
    ]
