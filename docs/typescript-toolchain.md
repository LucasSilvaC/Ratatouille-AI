# TypeScript 7 com ferramentas que usam a API do TypeScript 6

O TypeScript 7.0 fornece o compilador nativo, mas ainda não oferece a API
JavaScript estável exigida pelo `typescript-eslint` e por ferramentas do Next.js.
O `typescript-eslint` 8.72.1 rejeita explicitamente a API do TypeScript 7.0.

Esta branch usa a configuração lado a lado recomendada pela Microsoft:

- `@typescript/native`: alias para `typescript@7.0.2`, que fornece o executável
  `tsc`. O comando `pnpm typecheck` usa o compilador 7.0.2.
- `typescript`: alias para `@typescript/typescript6@6.0.2`, que fornece a API
  compatível para ESLint e Next.js, além do executável `tsc6`.

Não há supressão de regras do ESLint nem desativação da verificação de tipos.
O Next.js mantém a verificação de tipos do build pela API compatível; o comando
independente de typecheck verifica o projeto com o compilador nativo.

Para conferir as duas versões, execute pela raiz:

```sh
pnpm --filter @ratatouille/web exec tsc --version
pnpm --filter @ratatouille/web exec tsc6 --version
pnpm lint
pnpm typecheck
pnpm build
```

Vitest e `@vitest/coverage-v8` também permanecem alinhados em 5.1.0, pois o provider
de cobertura declara uma dependência de peer exata do runner.

Quando as ferramentas usadas pelo projeto suportarem a API do TypeScript 7,
reavalie a remoção dos aliases em conjunto. Não substitua apenas a entrada
`typescript` sem verificar lint, typecheck e build.

Referência: [Microsoft — Running Side-by-Side with TypeScript 6.0](https://devblogs.microsoft.com/typescript/announcing-typescript-7-0/#running-side-by-side-with-typescript-60).
