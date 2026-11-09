# Design do RatatouilleAI

Documentação de design v1 — 8 de novembro de 2026. A especificação inicial foi entregue em Markdown. A prévia HTML independente foi adicionada depois, sem alterar o código do web-app ou integrar serviços.

## Prévia HTML

Abrir [preview.html](preview.html) no navegador. O arquivo demonstra cardápio por dia e semana, edição de perfil, revisão de trocas com Cancelar/Aprovar e galeria de componentes. Todas as alterações existem apenas em memória e são perdidas ao recarregar.

As imagens ficam em `assets/`; manter essa pasta ao copiar o HTML. As fontes são carregadas do Google Fonts; sem internet, a prévia usa fontes sans-serif do sistema. Fotografias ilustrativas obtidas do Unsplash, com arquivos de origem registrados em [assets/README.md](assets/README.md). Não há validação nutricional, de alergênicos ou integração de IA.

Ver [preview-qa.md](preview-qa.md) para o estado de verificação e limites da prévia.

## Ordem de leitura

1. [DESIGN.md](DESIGN.md): referência central da identidade e linguagem visual.
2. [Produto e referências](produto-e-referencias.md): contexto, evidências e limites.
3. [Tokens](tokens.md): valores de cores, tipografia, espaçamento e movimento.
4. [Componentes](componentes.md): contratos reutilizáveis, sobretudo Cancelar/Aprovar.
5. [Telas e fluxos](telas-e-fluxos.md): estrutura e comportamento planejados.
6. [Template de tela](template-de-tela.md): modelo para especificar novas telas.
7. [Checklist](checklist.md): critérios para a futura implementação.

## Como usar

Antes de implementar uma tela, ler DESIGN.md, tokens e componentes; preencher uma cópia do template de tela e verificar o checklist. Usar as decisões deste diretório em todas as páginas. Mudanças globais devem atualizar primeiro os documentos correspondentes.

Estas especificações definem o design proposto, ainda sem validação visual em navegador ou pesquisa com usuários. O código existente conserva seu tema atual. Não confundir a documentação com funcionalidade disponível.

## Precedência

Requisitos do usuário > regras de domínio e acessibilidade > componentes > tokens > composição da tela > referências de inspiração. DESIGN.md resume a direção; os documentos especializados detalham seus contratos. Corrigir divergências antes de implementar.
