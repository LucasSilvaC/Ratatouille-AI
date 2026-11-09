# Componentes e padrões de interação

## Par obrigatório: Cancelar / Aprovar

Toda revisão que confirma uma alteração de perfil, preferências, plano ou refeição usa estes dois botões. Os rótulos visíveis são exatamente **Cancelar** e **Aprovar**. O título e o resumo do contexto explicam o objeto da aprovação; por exemplo, “Aprovar troca do almoço de terça-feira?”.

| Propriedade    | Cancelar                                    | Aprovar                                  |
| -------------- | ------------------------------------------- | ---------------------------------------- |
| Papel          | Abandonar proposta e manter versão aprovada | Confirmar e persistir a proposta exibida |
| Variante       | Secundário com contorno                     | Primário sólido                          |
| Fundo / texto  | Branco / text                               | primary / branco                         |
| Borda          | border-control, 1 px                        | primary, 1 px                            |
| Hover          | surface-muted                               | primary-hover                            |
| Pressionado    | disabled-bg com texto normal                | primary-pressed                          |
| Ícone opcional | X, antes do texto                           | Check, antes do texto                    |

Altura mínima 48 px, raio 12 px, padding horizontal 20 px e largura mínima 120 px. Texto 14 px/600. Se houver ícones, usar 18 px e gap de 8 px nos dois botões. Não depender do ícone para o significado.

Desktop: grupo alinhado à direita, Cancelar à esquerda e Aprovar à direita. Celular: manter a mesma ordem, duas colunas iguais quando couber; em larguras menores ou texto ampliado, empilhar Cancelar antes de Aprovar. Não inverter visualmente a ordem do teclado. Nunca espalhar os dois botões por regiões distantes.

### Estados e persistência

- Padrão, hover, pressionado e foco visível em ambas as variantes. Foco com anel de 2 px em focus e afastamento de 2 px.
- Aprovar desabilitado quando a proposta é inválida, não mudou ou ainda não foi validada. Explicar a razão junto ao grupo; tooltip não basta.
- Após Aprovar, manter o rótulo e mostrar spinner com mensagem “Salvando alterações…”. Bloquear novos envios e Cancelar durante a persistência curta. Não bloquear a página indefinidamente: em falha ou timeout, restaurar controles e informar o resultado conhecido.
- Aprovação só termina após confirmação de persistência. Em resultado incerto, consultar o estado antes de repetir; não emitir sucesso antecipado.
- Erro mantém a proposta para nova tentativa. Conflito de versão exige recarregar e revisar as diferenças antes de aprovar novamente.
- Cancelar descarta apenas a proposta em revisão e devolve foco ao acionador. Não deve apagar o perfil ou plano salvo.
- Em formulários longos, Cancelar abre confirmação somente se houver mudanças não salvas. Esse diálogo também usa Cancelar/Aprovar, com texto “Descartar alterações?” e explicação de que Aprovar descarta o rascunho. Cancelar retorna à edição.

### Limites do padrão

Voltar e Continuar são navegação do onboarding, não descarte/aprovação. Gerar cardápio e Trocar refeição iniciam uma proposta, sem persistir a substituição automaticamente. Esses controles usam as mesmas variantes primária e secundária; não criar estilos de botão por tela.

Cancelar nunca recebe vermelho. Em uma eventual confirmação destrutiva, Aprovar pode usar danger, com título que descreva explicitamente a perda. Exclusão de conta ou outros fluxos destrutivos não estão no escopo atual.

## Campos e seleção

Label permanente acima do campo; placeholder apenas como exemplo. Instrução e erro abaixo, associados ao campo. Indicar obrigatório em texto e não apenas com asterisco. Campo numérico inclui unidade visível. Não inserir valores pessoais fictícios em formulário real.

Chips de preferência são seleções múltiplas, com contorno, check e estado anunciado. Cards de região funcionam como grupo de seleção única. Restrições usam controles acessíveis próprios, agrupados por alergias, intolerâncias, condições e escolhas alimentares. Usar texto completo e não apenas ícone.

## Cards de refeição

Ordem: período → foto opcional → nome do prato → ingredientes principais → porções e estimativas disponíveis → restrições relevantes → ação “Trocar refeição”. Não exibir avaliações, preço, frete ou carrinho. A foto tem proporção 4:3, recorte consistente e alternativa textual contextual; não tratar fotografia como evidência dos ingredientes.

Sem foto: usar composição textual limpa com período e ingredientes, sem imagem quebrada ou fotografia de outro prato. Nome pode quebrar linha; ingredientes não ficam ocultos por truncamento essencial. Card não é inteiramente clicável se contém controles internos.

## Navegação

Stepper de quatro etapas com título e posição atual. Etapas concluídas podem ser revisitadas sem perder o rascunho. Calendário usa seletor de dias com data, estado selecionado e navegação de teclado. No celular, exibir “Dia” e “Semana” como escolhas claras se ambas as visualizações existirem; não exigir gesto de arrastar.

## Diálogo de revisão

Título específico, resumo “Atual” e “Proposta”, diferenças relevantes e par Cancelar/Aprovar. Nunca usar apenas a pergunta “Tem certeza?”. Foco inicial no título ou conteúdo; conter foco no diálogo, permitir Escape como Cancelar antes do envio e devolver foco ao acionador. Clique no fundo não descarta alterações silenciosamente.

## Feedback

Carregamento com mensagem real de progresso e skeleton apenas onde haverá conteúdo. Erros de campo ficam no campo e em resumo quando necessário. Avisos persistentes ficam em banners. Toast é complementar, com anúncio acessível; não é o único lugar para falha ou informação crítica.

Revisão bem-sucedida: “Troca aprovada. Almoço de terça-feira atualizado.” Cancelamento: fechar revisão e preservar plano. Nenhuma mensagem deve afirmar compatibilidade validada enquanto o serviço responsável estiver indisponível.
