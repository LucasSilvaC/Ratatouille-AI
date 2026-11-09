# Componentes por feature

As features usam Atomic Design para a camada visual e MVVM para separar estado
e regras de domínio. Os dois padrões são complementares.

```text
features/planner/
  components/
    molecules/   # MealCard, OnboardingStepper e ScenarioSelector
    organisms/   # formulários, seletores, comparação e calendário
    templates/   # AppShell: estrutura visual específica desta feature
    pages/       # PlannerApp e ComponentGallery
  providers/     # contexto compartilhado; não é uma unidade visual
  viewmodels/    # hooks de estado e comandos, sem JSX
  model/         # entidades, contratos e regras puras
  data/          # fixtures e adaptadores
  composition.ts
```

- **Atoms**: primitives genéricos compartilhados em `src/components/atoms`,
  inclusive os componentes shadcn/ui. Não duplicá-los dentro de cada feature.
- **Molecules**: pequenas composições de atoms com uma responsabilidade própria.
- **Organisms**: seções completas que agrupam controles ou molecules, como os
  formulários, o plano semanal e a comparação de refeições.
- **Templates**: estrutura e regiões das telas. Templates que dependem do estado
  de uma feature ficam nessa feature, em vez de `src/components`.
- **Pages**: composição final da experiência. Os arquivos do App Router em
  `src/app` apenas selecionam e renderizam essas páginas.

Criar somente níveis que tenham componentes reais. A feature `example` conserva
seu formulário em `components/organisms`, sem criar camadas vazias. Imports entre
níveis usam o alias `@/` para manter os caminhos explícitos.

Componentes genéricos de outras features devem continuar em `src/components`.
Não mover providers, regras ou ViewModels para pastas visuais para satisfazer a
hierarquia: eles têm responsabilidades distintas.
