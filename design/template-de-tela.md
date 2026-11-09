# Template reutilizável de especificação de tela

Copiar este documento para especificar uma tela futura. Preencher os campos antes da implementação. Os tokens e o par Cancelar/Aprovar vêm do sistema compartilhado; não redefini-los localmente.

## Identificação

- Nome da tela: [nome]
- Status: [rascunho / revisada / pronta para implementação]
- Objetivo do usuário: [resultado concreto]
- Entrada no fluxo: [origem]
- Saída esperada: [destino ou estado]
- Fontes de contexto: [documentos e referências]

## Conteúdo e hierarquia

| Ordem | Região             | Conteúdo                    | Componente compartilhado |
| ----- | ------------------ | --------------------------- | ------------------------ |
| 1     | Cabeçalho          | [marca, navegação ou etapa] | [componente]             |
| 2     | Título e descrição | [texto final]               | [componente]             |
| 3     | Conteúdo principal | [campos, cards ou seleção]  | [componente]             |
| 4     | Ações              | [ações e consequências]     | [componente]             |
| 5     | Feedback           | [aviso ou resultado]        | [componente]             |

## Dados

| Informação | Origem               | Obrigatória?       | Validação        | Vazio ou indisponível |
| ---------- | -------------------- | ------------------ | ---------------- | --------------------- |
| [dado]     | [serviço ou usuário] | [sim/não e motivo] | [regra validada] | [comportamento]       |

## Ações e persistência

- Ação que inicia a proposta: [rótulo e efeito]
- Contexto da confirmação: [título e diferenças visíveis]
- Cancelar: [rascunho descartado, dados preservados e destino do foco]
- Aprovar: [escopo exato persistido e condição de sucesso]
- Falha ou conflito: [estado preservado e recuperação]
- Navegação separada: [Voltar/Continuar, se aplicável]

## Estados

| Estado       | O que aparece                   | Ações disponíveis | Mensagem acessível |
| ------------ | ------------------------------- | ----------------- | ------------------ |
| Inicial      | [conteúdo]                      | [ações]           | [texto]            |
| Carregando   | [conteúdo preservado/progresso] | [ações]           | [texto]            |
| Vazio        | [orientação]                    | [próximo passo]   | [texto]            |
| Inválido     | [erros associados]              | [correção]        | [texto]            |
| Erro         | [escopo da falha]               | [recuperação]     | [texto]            |
| Sucesso      | [resultado confirmado]          | [continuidade]    | [texto]            |
| Indisponível | [limitação real]                | [alternativas]    | [texto]            |

## Responsividade e acessibilidade

- Celular: [ordem, largura, ações e seletor]
- Tablet/desktop: [colunas, limites e alinhamento]
- Teclado e foco: [ordem, entrada e retorno]
- Leitor de tela: [labels, estados e anúncios]
- Texto ampliado e movimento reduzido: [adaptação]

## Critérios de aceite

- [ ] Objetivo principal pode ser concluído.
- [ ] Estados e persistência estão definidos sem perda silenciosa.
- [ ] Cancelar/Aprovar seguem [componentes.md](componentes.md).
- [ ] Tokens seguem [tokens.md](tokens.md).
- [ ] Conteúdo, dados e alegações correspondem às capacidades reais.
- [ ] [Checklist compartilhado](checklist.md) revisado.

## Pendências

[Questões de produto, conteúdo, dados ou domínio que impedem fechar esta tela. Não substituir por suposições invisíveis.]
