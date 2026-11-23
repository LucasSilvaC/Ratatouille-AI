from importlib import import_module

from django.db import migrations, models
from django.db.models.deletion import PROTECT


SCHEMA_ANTERIOR = dict(import_module(".0001_initial", __package__).SCHEMA)
USUARIO = (
    SCHEMA_ANTERIOR["usuarios"]
    .replace("CREATE TABLE usuarios", "CREATE TABLE usuario")
    .replace("disposicao INTEGER CHECK(disposicao IN (0,1))", "disposicao TEXT")
)
RESPOSTAS = SCHEMA_ANTERIOR["respostas"].replace(
    "categoria TEXT NOT NULL",
    "usuario_id TEXT NOT NULL REFERENCES usuario(id), "
    "pergunta_id TEXT NOT NULL REFERENCES perguntas(id)",
)
INDICES_RESPOSTAS = {
    "idx_respostas_usuario": "CREATE INDEX idx_respostas_usuario ON respostas(usuario_id)",
    "idx_respostas_pergunta": "CREATE INDEX idx_respostas_pergunta ON respostas(pergunta_id)",
}
SCHEMA_ATUAL = {
    "classes": SCHEMA_ANTERIOR["classes"],
    "alimento": SCHEMA_ANTERIOR["alimentos"].replace("TABLE alimentos", "TABLE alimento"),
    "nutriente": SCHEMA_ANTERIOR["nutrientes"].replace("TABLE nutrientes", "TABLE nutriente"),
    "idx_alimentos_classe": SCHEMA_ANTERIOR["idx_alimentos_classe"].replace(
        "ON alimentos", "ON alimento"
    ),
    "alimento_nutrientes": SCHEMA_ANTERIOR["alimento_nutrientes"]
    .replace("REFERENCES alimentos", "REFERENCES alimento")
    .replace("REFERENCES nutrientes", "REFERENCES nutriente"),
    "idx_an_alimento": SCHEMA_ANTERIOR["idx_an_alimento"],
    "idx_an_nutriente_valor": SCHEMA_ANTERIOR["idx_an_nutriente_valor"],
    "perguntas": SCHEMA_ANTERIOR["perguntas"],
    "usuario": USUARIO,
    "respostas": RESPOSTAS,
    **INDICES_RESPOSTAS,
}


def schema_atual(existing):
    if {"usuarios", "alimentos", "nutrientes"} & existing.keys():
        return False
    existing = dict(existing)
    if "usuario" in existing:
        existing["usuario"] = existing["usuario"].replace("disposicao REAL", "disposicao TEXT")
    return all(
        " ".join(existing.get(name, "").replace('"', "").split())
        == " ".join(sql.replace('"', "").split())
        for name, sql in SCHEMA_ATUAL.items()
    )


def remodelar(apps, schema_editor):
    with schema_editor.connection.cursor() as cursor:
        cursor.execute("SELECT name, sql FROM sqlite_schema WHERE sql IS NOT NULL")
        existing = dict(cursor.fetchall())
        consolidada = import_module(".0004_consolidar_usuario_codigo", __package__)
        if consolidada.schema_consolidado(existing):
            return
        atualizado = schema_atual(existing)
        if not atualizado:
            cursor.execute("SELECT 1 FROM respostas LIMIT 1")
            if cursor.fetchone():
                raise RuntimeError("As respostas legadas precisam de mapeamento para usuário e pergunta.")

    tabela_nutriente = "nutriente" if atualizado else "nutrientes"
    schema_editor.execute("DELETE FROM alimento_nutrientes WHERE nutriente_id IN (7, 10)")
    schema_editor.execute(f"DELETE FROM {tabela_nutriente} WHERE id IN (7, 10)")
    if atualizado:
        return

    schema_editor.execute("ALTER TABLE alimentos RENAME TO alimento")
    schema_editor.execute("ALTER TABLE nutrientes RENAME TO nutriente")
    schema_editor.execute("ALTER TABLE usuarios RENAME TO usuarios_legado")
    schema_editor.execute(USUARIO)
    schema_editor.execute(
        "INSERT INTO usuario (id, nome, idade, senha, genero, peso, altura, disposicao) "
        "SELECT id, nome, idade, senha, genero, peso, altura, CAST(disposicao AS TEXT) "
        "FROM usuarios_legado"
    )
    schema_editor.execute("DROP TABLE usuarios_legado")
    schema_editor.execute("DROP TABLE respostas")
    schema_editor.execute(RESPOSTAS)
    for sql in INDICES_RESPOSTAS.values():
        schema_editor.execute(sql)


class Migration(migrations.Migration):
    dependencies = [("api", "0001_initial")]

    operations = [
        migrations.SeparateDatabaseAndState(
            database_operations=[migrations.RunPython(remodelar)],
            state_operations=[
                migrations.AlterModelTable(name="alimento", table="alimento"),
                migrations.AlterModelTable(name="nutriente", table="nutriente"),
                migrations.AlterModelTable(name="usuario", table="usuario"),
                migrations.RemoveConstraint(
                    model_name="usuario", name="usuario_disposicao_valida"
                ),
                migrations.AlterField(
                    model_name="usuario", name="disposicao", field=models.TextField(null=True)
                ),
                migrations.RemoveField(model_name="resposta", name="categoria"),
                migrations.AddField(
                    model_name="resposta",
                    name="usuario",
                    field=models.ForeignKey(to="api.usuario", on_delete=PROTECT, db_index=False),
                ),
                migrations.AddField(
                    model_name="resposta",
                    name="pergunta",
                    field=models.ForeignKey(to="api.pergunta", on_delete=PROTECT, db_index=False),
                ),
                migrations.AddIndex(
                    model_name="resposta",
                    index=models.Index(fields=["usuario"], name="idx_respostas_usuario"),
                ),
                migrations.AddIndex(
                    model_name="resposta",
                    index=models.Index(fields=["pergunta"], name="idx_respostas_pergunta"),
                ),
            ],
        ),
    ]
