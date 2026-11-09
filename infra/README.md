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

`pnpm infra:up` constrói o web-app e a imagem de migração, aguarda o PostgreSQL,
aplica as migrações e inicia o app. Os padrões funcionam sem arquivo de ambiente.
Para ajustar portas e credenciais, copie `infra/.env.example` para `infra/.env` antes
de iniciar. O arquivo `.env` é local e ignorado pelo Git.

Comandos disponíveis pela raiz:

| Comando                   | Ação                                                     |
| ------------------------- | -------------------------------------------------------- |
| `pnpm infra:up`           | Sobe o stack implementado e constrói as imagens.         |
| `pnpm infra:db`           | Sobe somente o PostgreSQL para desenvolvimento local.    |
| `pnpm infra:ps`           | Mostra o estado dos serviços.                            |
| `pnpm infra:logs`         | Acompanha os logs do Compose.                            |
| `pnpm infra:down`         | Para os serviços e mantém os dados do volume.            |
| `pnpm infra:down:volumes` | Para os serviços e apaga os dados persistidos do volume. |

Para desenvolver o app na máquina, use `pnpm infra:db`, `pnpm db:migrate` e
`pnpm dev`. Os comandos locais carregam o mesmo `infra/.env`; sem esse arquivo,
usam os padrões descritos em `infra/.env.example`.

Nos comandos locais, `DATABASE_URL` é montada a partir das variáveis `POSTGRES_*`.
Se precisar usar outro banco fora do Compose, defina `DATABASE_URL` em `infra/.env`.
Dentro dos containers, o Compose monta a URL com o host interno `postgres`.

## Layout

- `compose.yaml`: serviços, dependências, health checks, volumes e portas.
- `docker/Dockerfile`: imagens e etapas de build do app e do migrador.
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

O Compose atual contém apenas PostgreSQL, migração Drizzle e o web-app. API Python,
worker, broker e serviços de IA devem ser adicionados aqui quando suas implementações
estiverem prontas; as pastas documentadas ainda não são serviços executáveis.
