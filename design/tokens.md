# Tokens de design

Valores normativos propostos para o tema claro. Nomes conceituais para futura implementação, sem alteração de CSS nesta etapa.

## Cores

| Token           | Valor     | Uso                                   |
| --------------- | --------- | ------------------------------------- |
| background      | `#FAF8F5` | Fundo geral                           |
| surface         | `#FFFFFF` | Cards, formulários e diálogos         |
| surface-muted   | `#F1EFEA` | Áreas secundárias e hover neutro      |
| text            | `#242A26` | Texto principal                       |
| text-muted      | `#5E6862` | Texto secundário                      |
| border          | `#E2E0D8` | Separadores e bordas decorativas      |
| border-control  | `#858A82` | Limite de campos e botões secundários |
| primary         | `#B9472B` | Aprovar e ação principal              |
| primary-hover   | `#9E3921` | Hover principal                       |
| primary-pressed | `#842E1C` | Pressionado principal                 |
| on-primary      | `#FFFFFF` | Texto da ação principal               |
| primary-soft    | `#FBECE5` | Destaque suave                        |
| herb            | `#2D6A4F` | Seleção e sucesso                     |
| herb-soft       | `#EAF3EC` | Fundo de seleção e sucesso            |
| warning         | `#795600` | Texto de aviso                        |
| warning-soft    | `#FFF3CC` | Fundo de aviso                        |
| danger          | `#B42318` | Erro e ação destrutiva                |
| danger-soft     | `#FDECEA` | Fundo de erro                         |
| focus           | `#245A96` | Anel de foco                          |
| disabled-bg     | `#E8E5DF` | Fundo desabilitado                    |
| disabled-text   | `#696D67` | Texto desabilitado                    |

Usar branco sobre primary e herb; text sobre superfícies claras; warning sobre warning-soft; danger sobre danger-soft. Nunca usar tons suaves como cor de texto sobre branco. Bordas decorativas não substituem border-control em controles que precisam de limite visível. Não comunicar estado somente por cor.

## Tipografia

Outfit para títulos e marca textual. Plus Jakarta Sans para corpo, legendas e controles. Fallback: sistema sans-serif. Reaproveita as famílias do protótipo; futuros arquivos de fonte devem ter licença verificada.

| Estilo           | Desktop | Celular | Peso / entrelinha |
| ---------------- | ------- | ------- | ----------------- |
| Título de página | 32 px   | 28 px   | 700 / 1,2         |
| Título de seção  | 24 px   | 22 px   | 600 / 1,3         |
| Título de card   | 18 px   | 18 px   | 600 / 1,4         |
| Corpo e input    | 16 px   | 16 px   | 400 / 1,5         |
| Botão e label    | 14 px   | 14 px   | 600 / 1,4         |
| Auxiliar         | 14 px   | 14 px   | 400 / 1,5         |
| Microtexto       | 12 px   | 12 px   | 500 / 1,5         |

Microtexto apenas para metadados dispensáveis; restrições, erros e instruções usam pelo menos 14 px. Números nutricionais com algarismos tabulares quando disponíveis. Unidades sempre explícitas: kg, cm, kcal.

## Espaço e forma

Escala: 4, 8, 12, 16, 24, 32, 48 e 64 px. Gap interno de campo 8 px; entre campos 24 px; entre seções 32–48 px. Card com padding de 24 px no desktop e 16 px no celular. Par de ações com gap de 12 px.

Raios: 8 px em miniaturas; 12 px em campos e botões; 16 px em cards; 24 px em painéis e diálogos; 999 px em chips. Borda de 1 px; seleção pode usar 2 px sem deslocar conteúdo.

Sombras: card `0 2px 8px rgba(31,36,33,0.05)`; painel elevado `0 8px 24px rgba(31,36,33,0.08)`; diálogo `0 16px 40px rgba(31,36,33,0.12)`. Não aplicar sombra em todo elemento.

## Grade e responsividade

| Faixa               | Margens | Composição                                               |
| ------------------- | ------- | -------------------------------------------------------- |
| 320–767 px          | 16 px   | Uma coluna; calendário por dia                           |
| 768–1023 px         | 24 px   | Até duas colunas; formulários preservam ordem de leitura |
| A partir de 1024 px | 32 px   | Calendário até três colunas; conteúdo máximo 1200 px     |

Formulário máximo 760 px. Campo e botão padrão com altura mínima 48 px; botão compacto 44 px; alvo interativo mínimo 44 × 44 px. Texto ampliado pode aumentar a altura. Diálogo máximo 560 px, margem externa mínima 16 px e rolagem interna quando necessário.

## Movimento

Hover/foco: 120–160 ms. Abrir diálogo: 180–220 ms com fade discreto. Sem animação que atrase uma ação. Respeitar preferência por movimento reduzido, retirando deslocamentos e animações decorativas. Não animar números para simular processamento de IA.
