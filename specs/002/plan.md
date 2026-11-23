# Plano da remodelagem SQLite

Plano aprovado.

1. Criar uma migração transacional do Django para converter o esquema existente e atualizar o estado dos modelos.
2. Interromper a migração de bases com respostas legadas até existir um mapeamento de cada resposta para usuário e pergunta. As duas bases locais inspecionadas têm zero respostas.
3. Excluir vínculos antes dos nutrientes, preservar o restante do catálogo e atualizar o SQLite de distribuição a partir de uma cópia validada. Alinhar os arquivos SQL e o seed ao esquema final.
4. Testar a criação em banco vazio, a atualização de uma cópia legada e a adoção da base de distribuição pelo Django. Verificar os dados preservados, o tipo de `disposicao`, as restrições das novas FKs e a ausência de referências órfãs.
5. Executar os testes da API e comparar com a verificação inicial. A configuração padrão referencia o modelo inexistente `api.User`. O teste existente passou em memória com `auth.User` definido apenas para a verificação.

A distribuição migrada contém 2.423 alimentos, 39 nutrientes e 87.076 vínculos. A reconstrução com o seed contém 87.184 vínculos após a remoção. O seed e o SQLite de entrada já tinham contagens diferentes.
