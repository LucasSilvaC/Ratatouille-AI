# Checklist para a futura implementação

Esta lista define verificações futuras. Não representa testes já executados na interface.

## Consistência visual

- [ ] Todas as telas usam os tokens compartilhados, sem novas cores arbitrárias.
- [ ] Outfit e Plus Jakarta Sans têm hierarquia e fallback coerentes.
- [ ] Cards, campos, botões e chips mantêm raios e espaçamentos definidos.
- [ ] Fotos têm recortes adequados, licença e relação com a refeição.
- [ ] Um único conjunto de ícones, sempre com nome acessível.
- [ ] Não há elementos de delivery ou métricas técnicas decorativas.

## Cancelar e Aprovar

- [ ] Toda revisão de alteração apresenta ambos os botões e contexto explícito.
- [ ] Cancelar preserva dados aprovados e devolve foco corretamente.
- [ ] Aprovar só confirma sucesso após persistência.
- [ ] Carregamento bloqueia envio duplicado e tem recuperação de falhas.
- [ ] Proposta inválida explica por que Aprovar está indisponível.
- [ ] Erros e conflitos preservam o rascunho.
- [ ] Ordem visual e de teclado coincide em todas as larguras.

## Fluxos de produto

- [ ] Perfil, região, preferências e semana preservam rascunhos entre etapas.
- [ ] Pular preferências não remove restrições.
- [ ] Nova geração não sobrescreve o plano antes da aprovação.
- [ ] Troca afeta apenas a refeição escolhida e totais relevantes.
- [ ] Sem alternativa compatível, a interface mantém o plano e explica o limite.
- [ ] Mudança de restrições invalida alegações antigas de compatibilidade.
- [ ] País sem cobertura não recebe região substituta silenciosa.
- [ ] Cancelamento não é interpretado como rejeição alimentar.

## Acessibilidade e adaptação

- [ ] Medir contraste na interface: texto normal ao menos 4,5:1; texto grande e elementos gráficos essenciais ao menos 3:1.
- [ ] Foco visível, navegação por teclado e ordem de leitura coerente.
- [ ] Alvos interativos de pelo menos 44 × 44 px, sem sobreposição.
- [ ] Labels, instruções, erros e estados de seleção anunciados corretamente.
- [ ] Diálogos contêm foco, permitem saída adequada e devolvem foco.
- [ ] Informações essenciais não dependem apenas de cor, hover ou fotografia.
- [ ] Verificar 320, 390, 768, 1024 e 1440 px, além de zoom de 200% e reflow equivalente a 320 px.
- [ ] Mensagens longas e nomes de pratos não são cortados.
- [ ] Rodapé de ações não cobre campos, teclado virtual ou conteúdo.
- [ ] Preferência de movimento reduzido respeitada.

## Conteúdo e capacidade real

- [ ] Dados demonstrativos identificados em protótipos futuros.
- [ ] Não há promessas clínicas, selos de segurança ou percentuais sem validação real.
- [ ] Estimativas nutricionais e estados pendentes estão identificados.
- [ ] Falhas, vazios e indisponibilidade têm orientação útil.
- [ ] Coleta de informações pessoais tem necessidade e finalidade definidas.
- [ ] Tema escuro só é considerado pronto após tokens e revisão próprios.

## Revisão visual futura

Comparar telas renderizadas com a direção acordada, em desktop e celular. Revisar estado padrão, carregamento, erro e revisão Cancelar/Aprovar. Registrar divergências e corrigir antes de expandir para novas telas.
