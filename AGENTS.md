# RatatouilleAI — instruções para agentes

## Contexto

- Monorepo pnpm para um app de planejamento alimentar.
- `apps/web` é o produto implementado: Next.js, TypeScript, interface e backend. A demo usa dados locais; ainda não há integração real de IA nem validação clínica.
- `apps/ai-api`, `apps/ai-worker`, `packages/agents`, `packages/recommendation`, `packages/neural` e `packages/ai-client` descrevem capacidades futuras. Confira o código antes de tratá-las como implementadas.
- Leia o README mais próximo da tarefa. Use [`docs/architecture.md`](docs/architecture.md) para decisões entre domínios e [`infra/README.md`](infra/README.md) para inicialização.

## Princípios

1. Faça mudanças pequenas, incrementais e compatíveis com a arquitetura existente. Preserve os limites entre app web, serviços Python, pacotes compartilhados e contratos.
2. No web-app, mantenha domínio independente de frameworks; aplicação coordena casos de uso; apresentação valida/adapta entradas; infraestrutura implementa Drizzle e PostgreSQL. Componentes de interface usam Server Actions e não acessam banco diretamente. Siga Atomic Design nos componentes.
3. Em fluxos de IA, imponha restrições alimentares obrigatórias em código determinístico. Modelos podem sugerir e explicar, mas não substituem validação, políticas ou autorização. Mantenha segredos no servidor e minimize dados pessoais enviados a provedores.
4. Toda configuração de ambiente, Compose, Dockerfile e inicialização de serviços pertence a `infra/`. Use `infra/.env`; não crie um segundo arquivo de ambiente no app. Acrescente serviços de forma componível e mantenha os existentes funcionais.
5. Mantenha dependências no `package.json` do pacote que as usa e use o lockfile/workspace pnpm da raiz. Não mova `node_modules` para `infra/`.
6. Siga instruções mais específicas, como `apps/web/AGENTS.md`, quando trabalhar em seus diretórios.

## Fluxo de trabalho

- Identifique o domínio e leia os arquivos e instruções locais antes de editar.
- Prefira a menor mudança coerente; evite criar abstrações, dependências ou infraestrutura sem necessidade concreta.
- Valide o trabalho com os comandos relevantes e informe o que foi executado, além de limitações ou integrações ainda planejadas.
- Nunca registre segredos. Não descreva uma capacidade planejada como funcional sem verificar sua implementação.

## Comandos principais

- Demo local: `pnpm install` e `pnpm dev` — não exige banco.
- Stack Docker: `pnpm infra:up`.
- Web local com PostgreSQL: `pnpm install`, `pnpm infra:db`, `pnpm db:migrate`, `pnpm dev`.
- Qualidade: `pnpm lint`, `pnpm typecheck`, `pnpm test:unit`; `pnpm check` executa a verificação abrangente.

Execute os comandos pela raiz. Configurações locais ficam em `infra/.env`; o exemplo versionado é `infra/.env.example`.
