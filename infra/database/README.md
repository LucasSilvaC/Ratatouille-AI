# PostgreSQL da API Django

## Inicialização

O serviço `api-db-init` do [Compose](../compose.yaml) executa
[`bootstrap-api.sql`](bootstrap-api.sql) antes de iniciar a API. O script
cria o banco e a credencial próprios do Django, se ainda não existirem.

`migrate` aplica o esquema. `seed_catalog` carrega o catálogo de
[`seed.json`](seed.json) quando as tabelas do catálogo estão vazias.
Veja os comandos no [guia da API](../../apps/api/README.md).

## Criptografia das respostas

O Django cifra o conteúdo com AES-GCM e protege a chave de cada resposta com a
chave pública RSA do AWS KMS. A API devolve apenas metadados ao titular.
O serviço interno dos agentes é o único com permissão `kms:Decrypt` nas
chaves autorizadas. A API pública recebe apenas o ARN e a chave pública. O
PostgreSQL continua permitindo filtrar por pergunta.

Provisione uma chave KMS RSA de uso `ENCRYPT_DECRYPT`. Use seu ARN em
`DJANGO_RESPONSE_KMS_KEY_ID` e configure a chave pública DER em Base64 no
ambiente da API. Obtenha-a com uma identidade de implantação:

```powershell
$env:DJANGO_RESPONSE_PUBLIC_KEY = aws kms get-public-key --key-id $env:DJANGO_RESPONSE_KMS_KEY_ID --query PublicKey --output text
```

Em desenvolvimento, pode-se usar uma chave RSA local de pelo menos 2.048 bits
com a parte privada fora da API. Preserve as chaves KMS anteriores enquanto
houver registros ou backups que dependam delas.

Para migrar respostas Fernet existentes, faça um backup criptografado, pare a
API antiga e disponibilize a chave anterior em
`DJANGO_LEGACY_RESPONSE_ENCRYPTION_KEYS` exclusivamente no processo de migração:

```powershell
docker compose --project-directory infra -f infra/compose.yaml build api
docker compose --project-directory infra -f infra/compose.yaml stop api
docker compose --project-directory infra -f infra/compose.yaml run --rm --entrypoint python -e DJANGO_PUBLIC_DEPLOYMENT=false -e DJANGO_LEGACY_RESPONSE_ENCRYPTION_KEYS api manage.py migrate
```

Remova a variável legada do ambiente operacional após migrar. A API monta o
volume novo `api-runtime-data` para deixar o volume antigo `api-data`, que pode
conter a chave Fernet, fora do container. Configure a `DJANGO_SECRET_KEY`
anterior antes de subir a API se precisar preservar sessões e tokens. Guarde as
chaves legadas separadamente se ainda houver backups que dependam delas.

## Volume e backups

O Compose guarda os dados em `postgres-data` e a chave do Django em `api-runtime-data`.
Confirme a criptografia do armazenamento e dos snapshots no host ou provedor.
Restrinja o acesso ao Docker, ao PostgreSQL e às cópias dos dados.

Para criar um backup criptografado, use Python, `pg_dump` e `age`. Configure
`PGDATABASE`, `PGUSER`, `PGHOST` e `PGPORT` com uma credencial de leitura,
use `PGPASSFILE` para a senha e defina `AGE_RECIPIENT` com a chave pública.
Guarde o backup fora do repositório e a chave privada em local separado.

```powershell
python infra/database/backup.py D:/backups/ratatouille-api.dump.age --recipient "$env:AGE_RECIPIENT"
```

Para testar a restauração, aponte `PGDATABASE` para uma base descartável e execute em Bash:

```bash
set -o pipefail
age --decrypt --identity "$ARQUIVO_CHAVE_AGE" "$BACKUP_AGE" >/dev/null &&
age --decrypt --identity "$ARQUIVO_CHAVE_AGE" "$BACKUP_AGE" |
  pg_restore --dbname="${PGDATABASE:?selecione a base de teste}" \
    --no-password --no-owner --no-acl --single-transaction
```

## Logs

Django e Gunicorn registram metadados como nível e status HTTP. O PostgreSQL
do Compose omite SQL e parâmetros na operação normal. Aplique a mesma política
no proxy e no coletor de logs.

## Coleta e acesso

- Prefira `opcoes`. Use `aceita_texto_livre: true` quando necessário, com até
  500 caracteres. Configure o formato das perguntas antigas antes de receber novas respostas.
- Pela API, a equipe vê apenas ID e nome de usuário de outras contas. A
  exclusão pelo titular remove o perfil e as respostas do banco operacional.
- As respostas ficam disponíveis até que o titular as exclua ou apague a conta.

Antes da coleta real, confirme a finalidade e a base legal. Ao restaurar um
backup, reaplique as exclusões antes de reabrir o acesso.
Consulte a [LGPD, arts. 6º e 11](https://www.planalto.gov.br/ccivil_03/_ato2015-2018/2018/lei/l13709compilado.htm).
