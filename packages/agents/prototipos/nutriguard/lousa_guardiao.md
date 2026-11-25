# Guardião — transcrição da lousa 1

Diagrama fiel ao que está desenhado na lousa. Trechos com leitura incerta estão marcados com `(?)`.

```mermaid
flowchart TD
    IN["Inputs do usuário<br/>(cadastro)"] --> GU

    subgraph GU["Guardião"]
        direction TB
        IF0{"IF<br/>(regras fixas)"}
        IF0 -- "Não atende" --> NA0["Não atender"]
        IF0 -- "Atende" --> LLM["LLM"]
        LLM --> REL["Relatório"]
        REL --> REV["Revisar exclusões (?)"]
    end

    subgraph IFS["Lado IF — regras determinísticas"]
        direction TB
        A{"IF Alergia"}
        A -- "Atende" --> A1["Excluir alimentos"]
        A1 --> A2["Disclaimer:<br/>contaminação cruzada"]
        A -- "else" --> ANA["Não atende"]

        D{"IF Doença"}
        D -- "Atende" --> E{"IF Exclusão = Sim"}
        E --> E1["Excluir / limitar<br/>(mostrar)"]
        D -- "Atende" --> J{"IF Ajuste = Sim"}
        J --> J1["Limitar<br/>(base RAG)"]
        D -- "else" --> DNA["Não atende"]

        PLUS{"Plus: tenho<br/>acompanhamento?"}
        PLUS -- "Sim" --> PL["Plano"]
    end

    subgraph LLMS["Lado LLM — prompt do Guardião"]
        direction TB
        P0["Você é o responsável por garantir<br/>a segurança e o bem-estar do usuário"]
        P0 --> P1["1. Analisar inputs (IFs)"]
        P1 --> P2["2. Buscar RAG<br/>[Doença] [Alergia]"]
        P2 --> P3["3. Metrificar ajustes e exclusões<br/>a partir do RAG + input"]
        P3 --> P4["4. Consolidar<br/>relatório · fontes (semelhança) · raciocínio"]
        P4 --> P5["5. Validar"]
        P5 --> OUT["Saída obrigatória:<br/>Validado · Relatório · RAG"]
    end

    IF0 -.-> IFS
    LLM -.-> LLMS
    P2 -. "ReAct" .-> REV

    OUT --> PLAN["Planejador<br/>prompt planejado:<br/>'Siga obrigatoriamente' + prompt do Guardião"]
```

## Leitura da lousa

| Parte | O que diz |
|---|---|
| Centro | Guardião → IF (se não atende, para) → LLM → relatório → revisar exclusões |
| Direita (IF) | Alergia: excluir + disclaimer ou não atende. Doença: exclusão e/ou ajuste (limitar com base no RAG) ou não atende. Plus: com acompanhamento profissional → plano |
| Esquerda (LLM) | Papel, 5 funções e saída obrigatória (Validado, Relatório, RAG) |
| Rodapé | Planejador recebe prompt planejado + "siga obrigatoriamente" + prompt do Guardião |

Leituras incertas:
- "Revisar exclusões", em vermelho no centro.
- "O Dr. Gatinho / RAG", ao lado de "Limitar"; interpretado como base RAG.
- Ligação do "ReAct": seta do RAG para o bloco central.
