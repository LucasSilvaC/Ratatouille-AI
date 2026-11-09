# Integração de dev com main

## Reconciliação do histórico

A `main` recebeu a arquitetura por squash no commit `8c987b8`. Seu conteúdo é
idêntico ao commit `66275a8` da `dev`, mas o squash não preservou os mesmos pais.
Depois, a `dev` recebeu as telas e a identidade visual em `3a0c488`.

Essa divergência de histórico fez o Git tentar reaplicar a migração do monorepo
ao integrar as branches, causando conflitos em configurações, lockfile, páginas
e componentes renomeados. A resolução preserva o conteúdo atual da `dev`, que já
contém a arquitetura da `main`, e registra a `main` como pai de um merge commit.

## Ordem dos pull requests

1. Abra `fix/integracao-dev-main` → `dev`.
2. Integre esse PR com **Create a merge commit**. O vínculo com o histórico da
   `main` precisa ser preservado; **Squash and merge** e **Rebase and merge**
   descartariam esse vínculo e poderiam fazer os conflitos reaparecerem.
3. Depois da integração e dos checks, abra `dev` → `main`.
4. Use **Create a merge commit** também nessa promoção para manter o histórico
   compartilhado entre as branches.

Se o repositório não permitir merge commits, habilite esse método antes de
integrar o primeiro PR. Esta alteração não modifica as configurações do GitHub.

Os IDs acima identificam as versões reconciliadas. Novos commits em `dev` ou
`main` devem ser considerados e validados novamente antes da promoção.
