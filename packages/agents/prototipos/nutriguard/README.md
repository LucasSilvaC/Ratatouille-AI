# Protótipo do NutriGuard (Guardião)

Protótipo do cadastro/triagem com a simulação do caminho da informação pelo Guardião.
**Não está integrado** ao web-app nem à Nutripédia: é uma página HTML única para discutir
o fluxo com o grupo. Os ingredientes e pratos são fictícios.

| Arquivo             | O que é                                                              |
| ------------------- | -------------------------------------------------------------------- |
| `cadastro.html`     | Formulário + Guardião em regras determinísticas + simulação do fluxo |
| `fluxo_guardiao.md` | Fluxo revisado do Guardião (Mermaid) e o que mudou em relação à lousa |
| `lousa_guardiao.md` | Transcrição da lousa 1 do Guardião (Mermaid), com leituras incertas  |

## Abrir

Abra `cadastro.html` no navegador. O diagrama usa o Mermaid por CDN, então precisa de
internet; sem ela, a linha do tempo da simulação continua funcionando.

A chave de LLM (Azure OpenAI ou OpenAI) é opcional e só é usada para mapear o texto livre
para as listas fechadas. Ela fica na memória da aba e é enviada direto do navegador ao
provedor. Sem chave, o protótipo usa um dicionário local. Não use uma chave de produção.

## O que o protótipo já decide em código

- Bloqueios iniciais: menor de 19 anos, gestante, amamentando.
- Status das 25 condições conforme a planilha de mapeamento (pior status vence).
- Alergia digitada fora da lista fechada bloqueia; intolerância digitada vira PARCIAL.
- O LLM só sugere IDs das listas; IDs inventados são descartados e o usuário confirma.
- Ingrediente sem metadado de alergênico é tratado como violação.
- Disclaimer de contaminação cruzada quando há alergia.

## Pontos a resolver antes de virar produto

- **Alergia ao leite (APLV) está mapeada para `sem_lactose`.** Isso não é seguro: produto
  zero lactose pode ter proteína do leite. O protótipo mostra um aviso, mas o schema do
  Montador precisa de uma restrição própria (por exemplo, `alergia_leite`).
- Alergia a trigo, centeio, cevada ou aveia vira `celiaco` (exclui todo glúten). É seguro,
  porém mais restritivo que o necessário; falta uma restrição por cereal.
- As regras e listas estão dentro do HTML. Para o Guardião real, elas devem sair para uma
  tabela versionada lida em código (Python), e o catálogo fictício deve ser trocado pela
  TBCA com a tabela de alergênicos.
- O schema `entrada_montador.schema.json` citado no código ainda não está neste repositório.
- O Mermaid é carregado sem versão exata (`mermaid@11`).
