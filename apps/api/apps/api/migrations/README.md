# Migrações do banco

Uma migração é um arquivo Python que registra como o esquema ou os dados mudam entre versões. O Django usa as dependências declaradas em cada arquivo para escolher a ordem e registra o que foi aplicado na tabela `django_migrations`.

Nesta API, a migração inicial também reconhece esquemas SQLite compatíveis. As migrações seguintes tratam conversão de dados e vínculos legados. A migração `0004` consolida a tabela antiga de usuários em `auth_user` e adiciona a regra de seis caracteres ao código do alimento. Algumas operações são irreversíveis porque removem dados ou incorporam tabelas antigas.

Ao mudar um modelo, rode `makemigrations api` e revise o arquivo gerado. Para uma mudança que converte dados, valide primeiro em uma cópia do SQLite com dados representativos. Mantenha o esquema de referência em `infra/database/schemas/` e a base de distribuição alinhados quando a alteração afeta esses arquivos.

Comandos a partir da raiz do repositório, usando o ambiente descrito no [guia da API](../../../README.md).

```powershell
apps/api/env/Scripts/python.exe apps/api/manage.py showmigrations api
apps/api/env/Scripts/python.exe apps/api/manage.py makemigrations --check --dry-run
apps/api/env/Scripts/python.exe apps/api/manage.py migrate --plan
```

`showmigrations` mostra o histórico aplicado. `makemigrations --check --dry-run` verifica se o modelo exige uma migração nova sem gravar arquivos. `migrate --plan` mostra o que seria aplicado ao banco configurado.
