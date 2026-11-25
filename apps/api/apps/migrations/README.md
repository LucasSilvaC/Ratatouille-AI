# Migrações do banco

Uma migração é um arquivo Python que registra como o esquema ou os dados mudam entre versões. O Django usa as dependências declaradas em cada arquivo para escolher a ordem e registra o que foi aplicado na tabela `django_migrations`.

As migrações da API definem o esquema PostgreSQL administrado pelo ORM do Django.
Ao mudar um modelo, rode `makemigrations api` e revise o arquivo gerado. Para uma
migração que altera dados existentes, valide primeiro em um banco isolado com dados
representativos. A carga inicial do catálogo é executada com `seed_catalog` depois
de `migrate`. Consulte o [guia do banco](../../../../infra/database/README.md).

Comandos a partir da raiz do repositório, usando o ambiente descrito no [guia da API](../../README.md).

```powershell
node infra/scripts/with-env.mjs apps/api/env/Scripts/python.exe apps/api/manage.py showmigrations api
node infra/scripts/with-env.mjs apps/api/env/Scripts/python.exe apps/api/manage.py makemigrations --check --dry-run
node infra/scripts/with-env.mjs apps/api/env/Scripts/python.exe apps/api/manage.py migrate --plan
```

`showmigrations` mostra o histórico aplicado. `makemigrations --check --dry-run` verifica se o modelo exige uma migração nova sem gravar arquivos. `migrate --plan` mostra o que seria aplicado ao banco configurado.
