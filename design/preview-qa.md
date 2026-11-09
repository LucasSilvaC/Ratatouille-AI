# Verificação da prévia HTML

Data: 8 de novembro de 2026.

## Escopo

Prévia independente em `preview.html`, baseada nos documentos deste diretório e nas referências de comida fornecidas na conversa. Não é implementação de produção nem reprodução exata de um único screenshot.

## Conferências locais

- Formatação com Prettier.
- Compilação sintática do JavaScript embutido com o parser do Node.js.
- Existência dos arquivos locais de fotografia.
- Revisão de código: navegação, seleção de dias, visão semanal, edição de perfil, chips e revisão de troca usam dados em memória, sem requisições ao backend.

## Limitação

O navegador in-app retornou `The browser access host is unavailable` ao tentar abrir a prévia. Não foi possível capturar screenshots, verificar carregamento das fontes, medir overflow ou testar interações no navegador. As conferências de código não substituem essa validação.

final result: blocked

## Próxima verificação visual

Abrir `preview.html` em desktop e celular; verificar layout a 390 e 1440 px, teclado, Escape e retorno do foco no diálogo, Cancelar preservando a refeição e Aprovar atualizando somente a escolhida. Fotografias são ilustrativas, inclusive depois de uma troca; o aviso permanece visível.
