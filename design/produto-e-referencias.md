# Produto e referências

## Objetivo

Ajudar pessoas a montar e revisar um cardápio semanal com alimentos da região, respeitando restrições declaradas e gostos. Hipótese de público inicial: adultos que planejam refeições domésticas no Brasil. Essa hipótese ainda precisa de validação.

## Fontes analisadas

| Fonte                                                                                                           | Evidência e uso                                                                                                                |
| --------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------ |
| `C:/Users/CUL7CA/Desktop/Eldorado/CNV/wireframe-prototype/index.html`                                           | Leitura do HTML, CSS e lógica: quatro etapas, IMC ilustrativo, regiões, questionário opcional, calendário e troca de refeições |
| `C:/Users/CUL7CA/Desktop/Eldorado/CNV/wireframe-prototype/arquitetura.html`                                     | Intenção conceitual de NutriGuard, Chef Regional e ranking de preferências; não comprova integrações                           |
| [Arquitetura do projeto](../docs/architecture.md)                                                               | Estado real e limites: serviços de IA e modelo neural ainda documentais; políticas e dados precisam de validação               |
| [README do projeto](../README.md)                                                                               | Web-app base existente; telas do wireframe ainda não implementadas                                                             |
| [getdesign.md](https://getdesign.md/) e [repositório associado](https://github.com/VoltAgent/awesome-design-md) | Método de documentar a linguagem visual em Markdown para orientar agentes                                                      |
| Anexo YumQuick                                                                                                  | Inspiração em calor visual, fotos, curvas e hierarquia das ações                                                               |
| Anexo Food Delivery UI Kit                                                                                      | Inspiração em cards claros, espaçamento, chips e destaque do alimento                                                          |

Consulta das fontes web em 8 de novembro de 2026. Os anexos foram fornecidos na conversa; não há cópias desses arquivos de imagem neste diretório. A análise do protótipo foi feita pelo código-fonte, sem auditoria visual ou testes de usabilidade.

## O que preservar e evoluir

Preservar o percurso em quatro etapas e a regionalidade. Preferências são opcionais; restrições não são equivalentes a gostos. Trocar uma refeição deve manter as demais. Mostrar a proposta antes de aplicá-la é uma decisão nova deste design, assim como a revisão explícita do primeiro plano.

Substituir o painel técnico de SQL, embeddings e pesos por informações úteis: “Preferências consideradas”, “Restrições verificadas” apenas quando verificadas de fato e “Por que esta sugestão?”. Não apresentar o diagrama de arquitetura como seção da navegação do produto.

## Escopo de telas

Perfil e restrições; país e região; preferências; geração e revisão do plano; calendário semanal; detalhe e revisão de troca; edição do perfil. Login, delivery, pagamentos, lista de compras, chat e receitas completas não fazem parte desta especificação inicial.

## Limites de produto

- Dados do protótipo, calorias e resultados de agentes são demonstrativos.
- Não inferir que gênero informa necessidades fisiológicas; a coleta e utilidade de cada dado devem ser decididas antes da implementação.
- Não reproduzir classificações de IMC ou metas calóricas como orientação clínica automática. Sua presença e redação dependem de validação do domínio.
- Separar alergias, intolerâncias, condições de saúde e escolhas alimentares na interface e nos dados.
- Cancelar uma troca não deve ser registrado automaticamente como rejeição do alimento.
- Sem candidatos compatíveis, explicar a limitação e manter o plano aprovado; nunca flexibilizar restrições automaticamente.

## Decisões ainda abertas

Validar campos obrigatórios, regras nutricionais, cobertura do catálogo fora do Brasil, disponibilidade de fotos licenciadas e política de armazenamento de dados sensíveis. Até existir cobertura real para outro país, informar a indisponibilidade e preservar a seleção, sem usar Sudeste como fallback invisível.
