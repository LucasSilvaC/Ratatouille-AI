# Infraestrutura e inicialização

Este diretório é a fonte única de configuração operacional e inicialização do
monorepo. Docker, Compose, variáveis locais e scripts de bootstrap ficam aqui.
Os comandos de desenvolvimento e banco na raiz carregam `infra/.env` por meio de
`infra/scripts/with-env.mjs`.

## Início rápido

Requisitos: Node 24, pnpm 11 e Docker Desktop (ou Docker Engine com Compose). O
comando `pnpm infra:up` instala as dependências dentro das imagens; não exige
`pnpm install` na máquina.

```powershell
pnpm infra:up
```

`pnpm infra:up` constrói e inicia o web-app e a API Django. Cada aplicação usa
sua própria base no PostgreSQL. O web-app aguarda as migrações do Drizzle.
A API executa `migrate` e `seed_catalog` antes de iniciar o Gunicorn.
Os padrões funcionam sem arquivo de ambiente.
Para ajustar portas e credenciais, copie `infra/.env.example` para `infra/.env` antes
de iniciar. O arquivo `.env` é local e ignorado pelo Git.

Comandos disponíveis pela raiz:

| Comando                     | Ação                                                     |
| --------------------------- | -------------------------------------------------------- |
| `pnpm infra:up`             | Sobe o stack implementado e constrói as imagens.         |
| `pnpm infra:db`             | Sobe somente o PostgreSQL para desenvolvimento local.    |
| `pnpm infra:db api-db-init` | Sobe o PostgreSQL e provisiona a base local da API.      |
| `pnpm infra:ps`             | Mostra o estado dos serviços.                            |
| `pnpm infra:logs`           | Acompanha os logs do Compose.                            |
| `pnpm infra:down`           | Para os serviços e mantém os dados do volume.            |
| `pnpm infra:down:volumes`   | Para os serviços e apaga os dados persistidos do volume. |

Para desenvolver o app na máquina, use `pnpm infra:db`, `pnpm db:migrate` e
`pnpm dev`. Os comandos locais carregam o mesmo `infra/.env`; sem esse arquivo,
usam os padrões descritos em `infra/.env.example`.

Nos comandos locais, `DATABASE_URL` é montada a partir das variáveis `POSTGRES_*`.
Se precisar usar outro banco fora do Compose, defina `DATABASE_URL` em `infra/.env`.
Dentro dos containers, o Compose monta a URL com o host interno `postgres`.

## API Django no Docker

Para construir e iniciar somente a API, execute pela raiz:

```powershell
pnpm infra:up api
```

A API atende na porta `API_PORT` (8000 por padrão) e oferece o Swagger em
`http://localhost:8000/api/swagger/`. O serviço `api-db-init` cria a base e a
credencial da API quando necessário. Os dados ficam no volume PostgreSQL
`postgres-data`. O seed carrega o catálogo quando suas tabelas estão vazias.
A primeira carga pode levar alguns minutos. A API inicia após a conclusão.
Faça backup da base antes de atualizar a API com migrações.

A API lê a configuração `DJANGO_DB_NAME`, `DJANGO_DB_USER`,
`DJANGO_DB_PASSWORD`, `DJANGO_DB_HOST` e `DJANGO_DB_PORT`. No Compose, a conexão
usa o host interno `postgres` e a porta 5432. No Django local, o host padrão é
`127.0.0.1` e a porta acompanha `POSTGRES_PORT` quando `DJANGO_DB_PORT` está
ausente.

Após o provisionamento, uma rotação de `DJANGO_DB_PASSWORD` exige atualizar a
senha da credencial no PostgreSQL e a configuração da API.

### Publicar por HTTPS

Defina `DJANGO_PUBLIC_DEPLOYMENT=true` e configure `DJANGO_ALLOWED_HOSTS`
com o domínio público da API em `infra/.env`. A porta da API é publicada
apenas em `127.0.0.1`. Execute um proxy HTTPS no mesmo host. O modo público
desabilita o Django Admin, ativa redirecionamento para HTTPS, HSTS e cookies
seguros. O health check interno usa `/api/health/`.

O Django confia em um único proxy. O proxy deve sobrescrever
`X-Forwarded-Proto` e `X-Forwarded-For` com o protocolo e IP da conexão
recebida, sem confiar em valores enviados pelo cliente. Exemplo de configuração
para Caddy no host, com um domínio que aponta para o servidor:

```caddyfile
api.example.com {
    reverse_proxy 127.0.0.1:8000 {
        header_up X-Forwarded-Proto {scheme}
        header_up X-Forwarded-For {remote_host}
    }
}
```

Os limites por IP são de 10 logins, 5 cadastros e 30 renovações de token por
minuto. O modo público compartilha os contadores entre workers via PostgreSQL.
O Compose cria a tabela de cache no início. Em uma instalação direta, execute
`manage.py createcachetable` após `migrate` antes de iniciar o servidor.

Defina uma `DJANGO_SECRET_KEY` estável ou mantenha a chave gerada no volume
`api-runtime-data`. Use as variáveis SMTP do mesmo arquivo para habilitar o envio real
de e-mails.

## Django local

Use o [guia da API](../apps/api/README.md) para provisionar a base PostgreSQL,
instalar as dependências e executar `migrate`, `seed_catalog` e `runserver`.
O [README do banco](database/README.md) descreve o esquema e o fixture.
Para manter as sessões entre reinicializações, exporte `DJANGO_SECRET_KEY` no
processo ou execute o servidor com o carregador de `infra/.env`.

Os endpoints REST ficam em `/api/`. Solicite a recuperação de senha com
`POST /api/redefinir_senha/` e o campo `email`. O link expira em uma hora.
Para entrega real, configure as variáveis SMTP de `infra/.env.example` no ambiente
do processo Django, inclua o domínio público em `DJANGO_ALLOWED_HOSTS` e use uma
`DJANGO_SECRET_KEY` estável. A recuperação nativa atende contas ativas com
e-mail cadastrado e senha utilizável.

## Layout

- `compose.yaml`: serviços, dependências, health checks, volumes e portas.
- `docker/Dockerfile`: imagens do web-app, do migrador e da API Django.
- `docker/Dockerfile.dockerignore`: arquivos excluídos do contexto de build.
- `.env.example`: variáveis locais compartilhadas entre Compose e comandos locais.
- `scripts/with-env.mjs`: carrega a configuração central e inicia comandos locais.
- `scripts/compose.mjs`: define o ponto único de entrada para comandos Compose.

`NEXT_PUBLIC_APP_URL` também é enviado como argumento ao build do Next.js, pois o
Next incorpora variáveis públicas no bundle durante a compilação.

Os `package.json` e o lockfile do pnpm permanecem na raiz e nos pacotes que possuem
dependências. Os diretórios `node_modules` são artefatos locais gerados pelo workspace
e ignorados pelo Git; não são configuração de inicialização e ficam fora de `infra/`.

## Regra de evolução incremental

O repositório deve crescer por incrementos pequenos e componíveis. Toda inicialização
de serviço — imagem, serviço Compose, variáveis, health check, dependências, migração
ou script de bootstrap — deve ser definida ou orquestrada neste diretório. Ao adicionar
um serviço, inclua apenas os recursos de infraestrutura necessários para ele e mantenha
os serviços existentes funcionais. Não replique configuração operacional dentro de
`apps/` ou em outro diretório de infraestrutura. O código, as dependências e os comandos
próprios de cada pacote continuam junto ao pacote; `infra/` define como o ambiente o
configura e o inicia.

Worker, broker e serviços de IA devem ser adicionados aqui quando suas
implementações estiverem prontas.
