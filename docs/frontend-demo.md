# Frontend demonstrativo do RatatouilleAI

## Abrir

Na raiz, execute `pnpm install` se necessário e `pnpm dev`. Abra
`http://localhost:3000`. A rota `/componentes` mostra os componentes reais do
produto. Não é necessário configurar banco, credenciais ou backend.

O loading compartilhado usa a logo SVG e animações CSS nas cores da marca.
`LoadingIndicator` e `BrandLoader` são usados nos carregamentos, nas aprovações e
no fallback de navegação do Next.js. A preferência de movimento reduzido desativa
as animações. O indicador anuncia o estado para leitores de tela; a ilustração
decorativa não gera anúncios repetidos.

### Reutilizar o loading em outras rotas

`apps/web/src/app/loading.tsx` é o fallback global do App Router, herdado pelas
rotas filhas enquanto o conteúdo aguarda. Não há uma página pública `/loading`.
Não é necessário adicionar atrasos artificiais às navegações já prontas.

Para declarar explicitamente o mesmo fallback em outro segmento:

```tsx
// src/app/minha-rota/loading.tsx
export { default } from "@/app/loading";
```

Para operações dentro de uma tela, importe o componente compartilhado:

```tsx
import { LoadingIndicator } from "@/components/molecules/loading-indicator";

// Exiba somente enquanto a operação estiver pendente.
<LoadingIndicator message="Carregando seu conteúdo…" />;

// Variante compacta para ações e áreas pequenas.
<LoadingIndicator message="Salvando alterações…" compact />;
```

`LoadingState`, em `components/molecules/planner-feedback.tsx`, combina o mesmo
indicador com skeletons quando esse contexto for adequado. As animações ficam
no CSS global; nenhum componente precisa copiar o SVG ou os keyframes.

O fluxo começa sem dados pessoais preenchidos. Use exclusivamente informações
fictícias. Preencha nome, revise as restrições, escolha Brasil e uma das cinco
regiões. As preferências são opcionais. A geração cria uma **proposta**: só
**Aprovar** confirma perfil e semana. **Cancelar** retorna às preferências.
O calendário contém 9 a 15 de novembro de 2026, três refeições por dia.

Todos os dados são mantidos em memória numa única instância por aba. Recarregar
reinicia a demonstração. O rodapé também permite restaurar o cenário inicial.
As fontes Outfit e Plus Jakarta Sans são servidas localmente pelos pacotes
Fontsource (OFL-1.1); não há solicitação de fontes a um serviço externo.
A foto do resumo é ilustrativa; sua origem está em
`apps/web/public/illustrations/README.md`. Os cards usam composição textual para
não atribuir uma foto genérica aos ingredientes de uma refeição específica.

## MVVM e fronteiras

Base de código: `apps/web/src/features/planner/`.

| Parte          | Arquivos e responsabilidade                                                                                                                                                                             |
| -------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Model          | `model/types.ts`, `model/rules.ts`: entidades e regras puras, sem React                                                                                                                                 |
| Contrato       | `model/contracts.ts`: `PlannerRepository`, operações assíncronas tipadas com IDs, versões e contexto explícitos                                                                                         |
| Fixtures       | `data/fixtures.ts`: catálogos, ingredientes, filtros e semana determinísticos                                                                                                                           |
| Adaptador      | `data/mock-planner-repository.ts`: fonte de verdade, propostas, latência, versionamento e cenários                                                                                                      |
| Composição     | `composition.ts`: instancia e exporta `plannerRepository`                                                                                                                                               |
| ViewModels     | `viewmodels/use-session.ts`, `use-onboarding.ts`, `use-profile-editor.ts`, `use-plan.ts`, `use-gallery.ts`: carregamento, comandos, rascunhos, validação e feedback, sem JSX nem importação de fixtures |
| Views          | `components/{molecules,organisms,templates,pages}/`: Atomic Design dentro da feature                                                                                                                    |
| Compartilhados | `src/components/atoms/`: primitives shadcn/ui; `molecules/planner-*`: feedback; o AppShell da feature fica em `features/planner/components/templates/app-shell.tsx`                                     |

A organização visual está detalhada em `apps/web/src/features/README.md`.

O provider em `features/planner/providers/planner-provider.tsx`, usado no layout,
preserva o perfil em edição ao navegar para o calendário ou
galeria. Perfil aprovado, rascunho, plano aprovado, proposta semanal e proposta de
troca são estados separados. Aprovar uma troca altera apenas o item selecionado;
cancelar não altera o aprovado. Aprovar perfil com restrições ou região diferentes
marca o plano como pendente de revalidação. Revalidação local apenas verifica os
filtros demonstrativos; nunca representa segurança clínica.

## Cenários para testar

Expanda **Cenários da demonstração** para selecionar o resultado da próxima
operação. O diálogo de troca também oferece o seletor, permitindo mudar para
Sucesso sem perder a proposta que falhou.

| Cenário        | Resultado                                                                                                                                                            |
| -------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Sucesso        | Gera ou confirma após a latência simulada (650 ms por padrão)                                                                                                        |
| Erro           | Falha antes da gravação e preserva os dados em revisão                                                                                                               |
| Sem candidatos | Geração vazia; não altera a semana atual. Aprovações existentes continuam usando os contratos de persistência                                                        |
| Conflito       | Ao aprovar, simula uma atualização concorrente, incrementa a versão real e preserva a proposta. Exige **Recarregar e revisar diferenças** antes de aprovar novamente |

Para ajustar a latência, altere a opção `latencyMs` na composição. Testes usam
instâncias isoladas com latência zero; os hooks do produto compartilham somente a
instância da composição. Os testes não dependem de sorte ou falhas aleatórias.

Países fora do Brasil não têm cobertura e não recebem região substituta. Os filtros
locais ilustram escolhas vegetarianas/veganas, lactose e frutos do mar. Condições
de saúde e doença celíaca retornam ausência de candidatos porque a demonstração
não tem capacidade de avaliá-las. Restrições nunca são removidas para gerar um
resultado. Os valores de kcal e porções são exemplos, sem cálculo nutricional.

Roteiro essencial: voltar no onboarding; pular preferências com restrições;
cancelar/aprovar uma troca; cancelar nova semana; provocar erro e conflito durante
aprovação; recarregar/revisar e tentar novamente; editar restrições e observar a
pendência do plano; navegar mantendo o rascunho; cancelar edição e confirmar ou
abandonar o descarte. No diálogo de descarte, Aprovar descarta o rascunho e
Cancelar retorna à edição.

## Substituir por API

Implemente `PlannerRepository` num novo adaptador HTTP e substitua **somente a
instanciação em `features/planner/composition.ts`**. Views e ViewModels continuam
dependendo do mesmo contrato. Não há cliente HTTP fictício nesta entrega.

O backend futuro deverá devolver IDs e versões, preservar a atomicidade de
`approveWeek` (perfil inicial e semana juntos), validar as restrições no servidor
e rejeitar versões antigas. `refreshWeekProposal` e `refreshMealProposal` devem
reconsultar a versão atual para uma nova revisão explícita, sem confirmar uma
proposta por conta própria. Os cenários demonstrativos são metadados de teste;
um adaptador real deve ignorá-los ou rejeitá-los fora de um ambiente de teste.
Não transportar estruturas de componentes React nem regras clínicas fictícias.

## Verificações

`pnpm check` executa formatação, ESLint, TypeScript, Vitest e build. `pnpm test:e2e`
executa os fluxos integrados no Chromium pelo Playwright. Os testes de domínio e
hooks ficam em `apps/web/tests/unit/planner-*.test.*`; os de navegador, em
`apps/web/tests/e2e/`. Nenhum deles acessa o banco.

Não há autenticação, integrações de IA, diagnóstico, lista de compras, delivery ou
pagamentos. A infraestrutura de exemplo existente permanece fora do fluxo do
produto. Nada é publicado ou enviado a serviços de produto externos.

Verificação desta entrega: 26 testes Vitest e 8 testes Playwright passaram, além
de formatação, ESLint, TypeScript e build. Houve inspeção das seis capturas
`apps/web/test-results/qa-*.png` (arquivos locais ignorados pelo Git). O Chromium
verificou ausência de overflow em 320, 390, 768, 1024 e 1440 px, recuperação de
falhas, bordas dos controles, contenção/retorno de foco e Escape, sem erros de
console. Não houve teste em aparelho físico, outros motores de navegador ou com
leitor de tela, nem auditoria formal de contraste de todos os estados.
