# Fluxo do Guardião (revisado)

```mermaid
flowchart TD
    A["Cadastro / Perfil<br/>(tags fechadas + texto livre)"] --> B{"Campos obrigatórios<br/>completos e válidos?"}
    B -- Não --> B1["Sinalizar pendência /<br/>pedir correção"] --> A
    B -- Sim --> C{"Bloqueio inicial?<br/>idade < 19, gestante,<br/>amamentando"}
    C -- Sim --> X["Bloquear planejamento<br/>+ encaminhar profissional"]
    C -- Não --> D{"Há texto livre?<br/>outra alergia/intolerância,<br/>não gosta"}
    D -- Sim --> D1["LLM sugere mapeamento<br/>para lista fechada"] --> D2{"Usuário confirma?"}
    D2 -- Não / sem mapeamento --> D3["Alergia fora da lista: bloquear<br/>Intolerância: PARCIAL + aviso<br/>Não gosta: só comparação por palavra"]
    D2 -- Sim --> E
    D3 --> E
    D -- Não --> E["Processamento paralelo"]

    E --> F1["Avaliador de condições<br/>status da tabela versionada"]
    E --> F2["Motor de alergias<br/>alergênicos + derivados"]
    E --> F3["Intolerâncias<br/>exclusões / limites"]
    E --> F4["Estilo alimentar e religioso<br/>vegetariano, kosher, halal..."]

    F1 --> F1R["RAG: só texto explicativo<br/>não decide status"]
    F1 --> G
    F2 --> G
    F3 --> G
    F4 --> G
    F1R --> G

    G["Consolidar resultados"] --> H{"Motor de regras<br/>pior status vence"}
    H -- "NÃO ATENDE (qualquer item)" --> X
    H -- ATENDE --> I1["Regras aplicáveis"]
    H -- PARCIAL --> I2["Escopo limitado<br/>+ avisos obrigatórios"]
    I1 --> J
    I2 --> J

    J{"Validador de segurança<br/>regras sem conflito?<br/>alimentos suficientes?<br/>disclaimer presente?"}
    J -- Não --> X
    J -- Sim --> K["Gerar política de segurança<br/>JSON versionado: status, restricoes,<br/>nao_misturar, avisos, versao_regras"]

    K --> DRI["Calculadora DRI<br/>EER e metas por refeição"] --> L["Enviar ao Planejador"]
    L --> M["Receber refeições montadas"]
    M --> N{"Violação?<br/>ingrediente x exclusões<br/>via metadados TBCA"}
    N -- Não --> P["Liberar plano<br/>+ disclaimer contaminação cruzada"]
    N -- Sim --> O{"Tentativas < N?"}
    O -- Sim --> O1["Rejeitar refeição<br/>pedir substituição"] --> L
    O -- Não --> X2["Plano seguro padrão<br/>ou bloquear"]

    N -. "Ingrediente sem metadado" .-> O1
```

## Mudanças em relação ao fluxo original

1. Bloqueios iniciais (idade, gestação, amamentação) antes do processamento.
2. LLM só mapeia texto livre para lista fechada; usuário confirma; LLM não decide status.
3. Status das condições vem da tabela versionada (planilha); RAG só explica.
4. Intolerâncias e estilo alimentar ganham caminho próprio.
5. Qualquer NÃO ATENDE bloqueia; pior status vence.
6. Validador de segurança com critérios explícitos.
7. PARCIAL gera escopo limitado com avisos obrigatórios.
8. Loop de substituição com limite de tentativas.
9. Ingrediente sem metadado de alergênico é tratado como violação.
