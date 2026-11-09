# RatatouilleAI — Design System

## Visão geral

Um caderno de cozinha contemporâneo para planejar a alimentação da semana com ingredientes regionais e preferências pessoais. O produto deve transmitir apetite, acolhimento e clareza. O cardápio é o centro da experiência; a tecnologia aparece quando ajuda a entender uma sugestão.

Esta é uma especificação própria no formato DESIGN.md, inspirada na abordagem do [getdesign.md](https://getdesign.md/): registrar cores, tipografia, espaçamento, componentes e suas razões para manter consistência nas próximas telas. Não é reprodução de um template comercial nem uma certificação de conformidade com uma especificação externa.

## Direção visual: cozinha regional contemporânea

Fundo creme, superfícies brancas, texto escuro e terracota como cor principal. Verde de ervas apoia seleções, informações de compatibilidade e sucesso. Pêssego e amarelo suave ficam em pequenos destaques. A comida fornece a maior parte da variedade de cores.

Das referências anexadas, aproveitar fotos apetitosas, cards arredondados, filtros compactos e ações reconhecíveis. Adaptar para um web-app de planejamento: evitar grandes áreas laranja, barras com ícones sem rótulos e elementos de compra ou entrega.

Do protótipo, preservar a sequência perfil → região → preferências → semana, as fontes Outfit/Plus Jakarta Sans e a combinação de neutros quentes com verde. A mudança proposta dá protagonismo à terracota e organiza confirmações em um padrão único.

## Linguagem visual

| Elemento          | Diretriz                                                          |
| ----------------- | ----------------------------------------------------------------- |
| Canvas            | Creme `#FAF8F5`; espaços amplos entre seções                      |
| Superfície        | Branco `#FFFFFF`, borda quente e sombra discreta                  |
| Ação principal    | Terracota `#B9472B`, texto branco                                 |
| Apoio             | Verde `#2D6A4F` sobre verde claro `#EAF3EC`                       |
| Texto             | `#242A26`; secundário `#5E6862`                                   |
| Títulos           | Outfit 600–700; frases curtas, sem caixa alta integral            |
| Corpo e controles | Plus Jakarta Sans 400–600, corpo de 16 px                         |
| Geometria         | Cards 16 px; painéis 24 px; controles 12 px; chips em pílula      |
| Fotografia        | Comida real, luz natural, louça simples, ingredientes brasileiros |
| Ícones            | Uma única biblioteca linear, preferencialmente Lucide, 20 px      |

Os valores completos estão em [tokens.md](tokens.md). Evitar gradientes decorativos, excesso de sombras, efeito vidro, emojis como sistema de ícones e métricas fictícias de IA.

## Composição

Cabeçalho compacto com marca textual e navegação legível. Onboarding em coluna central de até 760 px; calendário em área de até 1200 px. Conteúdo com alinhamento à esquerda. A fotografia deve apoiar a identificação da refeição sem empurrar ingredientes e ações para fora da tela.

No desktop, a semana pode usar cards diários em grade de três colunas. No celular, abrir o dia selecionado em uma coluna, com seletor de dias acessível. Não reduzir sete colunas até o texto ficar ilegível.

## Assinatura dos componentes

Toda confirmação de alteração usa o par **Cancelar / Aprovar**: Cancelar é secundário com contorno; Aprovar é primário em terracota. Mesma altura, raio e linguagem em todos os contextos. O título explica o que será aprovado. Ver comportamento completo em [componentes.md](componentes.md).

Navegação e descoberta podem ter rótulos próprios, como Voltar, Continuar, Gerar cardápio e Trocar refeição, usando as mesmas variantes visuais. Nunca chamar Cancelar de Voltar: as ações têm efeitos diferentes.

## Voz

Português brasileiro, próximo e objetivo. Exemplos: “Sua semana, do seu jeito”, “O que você gosta de comer?”, “Revisar troca do almoço de terça-feira”. Identificar estimativas e explicar indisponibilidade sem prometer resultados clínicos. Não usar “100% seguro”, “peso ideal” ou porcentagens de afinidade sem suporte real.

## Estados e confiança

Toda tela deve prever carregamento, vazio, erro, sucesso e indisponibilidade quando aplicável. Uma proposta permanece em revisão até Aprovar concluir a persistência. Cancelar preserva os dados aprovados. Restrições têm prioridade sobre preferências e nunca são relaxadas silenciosamente.

## Continuidade

Aplicar este sistema aos componentes atômicos existentes no futuro, preservando Atomic Design e a arquitetura do repositório. Tema claro é a referência inicial. O tema escuro existente precisa de especificação equivalente antes de ser apresentado como parte deste novo sistema.
