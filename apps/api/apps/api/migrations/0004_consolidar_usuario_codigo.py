from importlib import import_module

import django.core.validators
import django.db.models.deletion
import django.db.models.functions.text
import django.db.models.lookups
from django.conf import settings
from django.contrib.auth.hashers import identify_hasher, make_password
from django.db import migrations, models


ANTERIOR = import_module(".0002_remodelar_catalogo_respostas", __package__)
ALIMENTO = ANTERIOR.SCHEMA_ATUAL["alimento"].replace(
    "codigo TEXT", "codigo VARCHAR(6)"
).replace(
    "REFERENCES classes(id))",
    "REFERENCES classes(id), CONSTRAINT alimento_codigo_seis CHECK (length(codigo) = 6))",
)
RESPOSTAS = ANTERIOR.RESPOSTAS.replace(
    "usuario_id TEXT NOT NULL REFERENCES usuario(id)",
    "usuario_id INTEGER NOT NULL REFERENCES auth_user(id)",
)
PERFIL = (
    ("nome", "TEXT NOT NULL DEFAULT ''"),
    ("idade", "INTEGER CONSTRAINT usuario_idade_valida CHECK (idade >= 0)"),
    ("genero", "TEXT"),
    ("peso", "REAL CONSTRAINT usuario_peso_valido CHECK (peso > 0)"),
    ("altura", "REAL CONSTRAINT usuario_altura_valida CHECK (altura > 0)"),
    ("disposicao", "REAL"),
)


def schema_consolidado(existing):
    if {"usuario", "usuarios", "alimentos", "nutrientes"} & existing.keys():
        return False
    expected = {**ANTERIOR.SCHEMA_ATUAL, "alimento": ALIMENTO, "respostas": RESPOSTAS}
    del expected["usuario"]
    if not {"auth_user", "auth_user_groups", "auth_user_user_permissions"} <= existing.keys():
        return False
    auth_sql = existing["auth_user"].replace('"', '')
    return all(f" {field} " in auth_sql for field, _ in PERFIL) and all(
        " ".join(existing.get(name, "").replace('"', "").split())
        == " ".join(sql.replace('"', "").split())
        for name, sql in expected.items()
    )


def senha_migrada(senha):
    try:
        identify_hasher(senha)
    except ValueError:
        return make_password(None)
    return senha


def consolidar(apps, schema_editor):
    connection = schema_editor.connection
    with connection.cursor() as cursor:
        cursor.execute("SELECT name, sql FROM sqlite_schema WHERE sql IS NOT NULL")
        existing = dict(cursor.fetchall())
        if schema_consolidado(existing):
            return
        cursor.execute("SELECT 1 FROM alimento WHERE length(codigo) <> 6 LIMIT 1")
        if cursor.fetchone():
            raise RuntimeError("Corrija os códigos de alimento que não têm seis caracteres.")

    user = apps.get_model("api", "User")
    if "auth_user" in existing:
        for campo, definicao in PERFIL:
            schema_editor.execute(f"ALTER TABLE auth_user ADD COLUMN {campo} {definicao}")
    else:
        schema_editor.create_model(user)

    alias = connection.alias
    accounts = user.objects.using(alias)
    usuarios = apps.get_model("api", "Usuario").objects.using(alias)
    for usuario in usuarios.iterator():
        if accounts.filter(username=usuario.id).exists():
            raise RuntimeError("O identificador de um usuário legado já é usado como username.")
        accounts.create(
            username=usuario.id,
            password=senha_migrada(usuario.senha),
            **{campo: getattr(usuario, campo) for campo, _ in PERFIL},
        )

    content_types = apps.get_model("contenttypes", "ContentType").objects.using(alias)
    content_types.filter(app_label="auth", model="user").update(app_label="api")

    schema_editor.execute(ALIMENTO.replace("CREATE TABLE alimento ", "CREATE TABLE alimento_novo "))
    schema_editor.execute(
        "INSERT INTO alimento_novo (codigo, descricao, classe_id) "
        "SELECT codigo, descricao, classe_id FROM alimento"
    )
    schema_editor.execute("DROP TABLE alimento")
    schema_editor.execute("ALTER TABLE alimento_novo RENAME TO alimento")
    schema_editor.execute(ANTERIOR.SCHEMA_ATUAL["idx_alimentos_classe"])

    schema_editor.execute(RESPOSTAS.replace("CREATE TABLE respostas ", "CREATE TABLE respostas_novas "))
    schema_editor.execute(
        "INSERT INTO respostas_novas (id, resposta, usuario_id, pergunta_id) "
        "SELECT respostas.id, respostas.resposta, auth_user.id, respostas.pergunta_id "
        "FROM respostas LEFT JOIN usuario ON usuario.id = respostas.usuario_id "
        "LEFT JOIN auth_user ON auth_user.username = usuario.id"
    )
    schema_editor.execute("DROP TABLE respostas")
    schema_editor.execute("ALTER TABLE respostas_novas RENAME TO respostas")
    for sql in ANTERIOR.INDICES_RESPOSTAS.values():
        schema_editor.execute(sql)
    schema_editor.execute("DROP TABLE usuario")



class Migration(migrations.Migration):
    dependencies = [("api", "0003_disposicao_real")]

    operations = [
        migrations.SeparateDatabaseAndState(
            database_operations=[migrations.RunPython(consolidar)],
            state_operations=[
                migrations.AlterField(
                    model_name='alimento',
                    name='codigo',
                    field=models.CharField(max_length=6, primary_key=True, serialize=False, validators=[django.core.validators.MinLengthValidator(6)]),
                ),
                migrations.AddConstraint(
                    model_name='alimento',
                    constraint=models.CheckConstraint(condition=django.db.models.lookups.Exact(django.db.models.functions.text.Length('codigo'), 6), name='alimento_codigo_seis'),
                ),
                migrations.AlterField(
                    model_name='resposta',
                    name='usuario',
                    field=models.ForeignKey(db_index=False, on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL),
                ),
                migrations.DeleteModel(
                    name='Usuario',
                ),
            ],
        ),
    ]
