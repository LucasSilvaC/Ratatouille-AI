# Telas e fluxos planejados

## Estrutura comum

Cabeçalho com RatatouilleAI em texto e acesso ao perfil quando existir. Onboarding exibe quatro etapas: Perfil, Região, Preferências e Cardápio. Cada página tem um título, breve orientação, conteúdo principal e ações. O calendário torna-se a área principal após a aprovação inicial.

Não há implementação de rotas nesta entrega. Os nomes abaixo representam telas e estados de design.

## 1. Perfil e restrições

Objetivo: registrar informações necessárias sem misturar preferências com restrições. Formulário central com nome e campos pessoais cuja necessidade seja validada pelo produto. Altura e peso, caso usados, têm unidade e orientação; valores não devem gerar diagnóstico visual automático.

Seções separadas: alergias, intolerâncias, condições de saúde e escolhas alimentares. Cada seção explica por que a informação é solicitada e pode indicar ausência de restrição. Não presumir ausência quando o usuário ainda não respondeu. Não reutilizar seleções fictícias do protótipo.

Ação principal “Continuar”; sem alterações persistidas automaticamente nesta proposta de fluxo. Rascunho mantido ao navegar entre etapas. Falhas não apagam campos. Erros impedem avanço somente nos dados realmente obrigatórios.

## 2. País e região

Objetivo: aproximar ingredientes da realidade local. País em seletor; Brasil revela cards Sudeste, Sul, Nordeste, Norte e Centro-Oeste. Cada card tem nome e exemplos breves, sem estereótipos visuais. Seleção única explícita.

“Voltar” e “Continuar” preservam rascunho. Quando o país não tiver catálogo suportado, explicar o limite e não avançar para um cardápio regional inventado. Não usar Sudeste como substituto silencioso.

## 3. Preferências

Objetivo: conhecer gostos, com possibilidade de pular. Grupos do protótipo: proteínas brancas, proteínas alternativas, carboidratos, vegetais e café da manhã. Opções incompatíveis com restrições ficam indisponíveis com razão legível.

Escolhas vazias significam preferência não informada; não significam desgosto. “Pular por enquanto” preserva restrições e segue para a geração. “Gerar cardápio” também inicia a geração. Antes de gerar, mostrar resumo compacto do perfil, região e restrições com opção de editar.

## 4. Geração e revisão inicial

Enquanto gera: manter contexto e exibir “Preparando sugestões para sua semana…”. Não apresentar tempos, etapas técnicas ou porcentagens fictícias. Em erro, oferecer nova tentativa preservando entradas. Sem candidatos válidos, explicar a limitação e apontar como revisar os dados, sem sugerir remover uma alergia.

Ao concluir: apresentar a semana como **Proposta**, com sete dias e café da manhã, almoço e jantar conforme o protótipo. Totais e porções só aparecem se disponíveis e identificados como estimativas quando necessário.

Revisão com par Cancelar/Aprovar. Cancelar retorna às preferências e preserva os dados do onboarding como rascunho. Aprovar confirma perfil, preferências e plano no fluxo proposto; somente sucesso confirmado abre o calendário como plano aprovado. O contrato de persistência deverá ser definido na implementação.

## 5. Calendário semanal

Cabeçalho “Sua semana, do seu jeito”, intervalo de datas e resumo da região. Ações “Editar perfil e preferências” e “Gerar nova proposta”. A semana existente permanece visível durante uma nova geração.

Desktop: cards diários em grade de até três colunas, com refeições empilhadas. Celular: seletor de dias e conteúdo do dia selecionado; início no dia atual quando estiver no intervalo, ou no primeiro dia do plano. Estado de seleção indicado por texto/forma e cor.

Sem plano: explicar a proposta e oferecer “Criar meu cardápio”. Erro de carregamento tem tentativa de recarga. Em plano desatualizado por mudança de restrições, mostrar aviso persistente e exigir revalidação antes de apresentar compatibilidade.

## 6. Troca de refeição

1. “Trocar refeição” inicia busca para uma refeição identificada por dia e período.
2. Manter a refeição atual; mostrar carregamento apenas no contexto da troca.
3. Abrir revisão com atual e proposta, ingredientes, porções e diferenças disponíveis.
4. Cancelar fecha sem alterar o plano. Aprovar aplica somente essa refeição e atualiza totais relevantes após confirmação do serviço.
5. Sem opção válida, informar isso e manter a atual. Em conflito com edição mais recente, recarregar e pedir nova revisão.

Não registrar cancelamento como desgosto. Um eventual feedback de gosto precisa de ação explícita e separada.

## 7. Edição de perfil e nova semana

Editar abre os dados atuais como rascunho, finalizando com Cancelar/Aprovar. Aprovar mudanças de restrições exige sinalizar que o plano anterior precisa de revalidação. Se ela falhar, manter informação de indisponibilidade/pendência, sem selo de compatibilidade antigo.

Gerar nova proposta nunca substitui a semana imediatamente. A revisão compara o escopo afetado, com Cancelar/Aprovar. Cancelar mantém o plano anterior. Aprovar confirma a versão revista; falha mantém ambos os contextos identificados, sem comunicar atualização concluída.

## Microcopy de referência

| Situação               | Texto                                                                  |
| ---------------------- | ---------------------------------------------------------------------- |
| Questionário opcional  | “Conte o que você gosta ou pule por enquanto.”                         |
| Revisão da troca       | “Revisar almoço de terça-feira”                                        |
| Confirmação contextual | “Ao aprovar, apenas esta refeição será substituída.”                   |
| Sem alternativas       | “Não encontramos outra opção compatível com as restrições informadas.” |
| Falha ao salvar        | “Não foi possível confirmar a alteração. Sua proposta continua aqui.”  |
| Dados estimados        | “Valores nutricionais estimados por porção.”                           |
