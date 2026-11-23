# Remodelagem do catálogo alimentar e das respostas

Esquema aprovado.

- Renomear as tabelas `usuarios`, `alimentos` e `nutrientes` para `usuario`, `alimento` e `nutriente`.
- Armazenar `usuario.disposicao` como `REAL` opcional. Converter textos numéricos existentes em valores de ponto flutuante, preservar valores nulos e interromper a migração caso existam textos inválidos.
- Substituir `respostas.categoria` por `usuario_id` e `pergunta_id`, chaves estrangeiras obrigatórias para `usuario.id` e `perguntas.id`.
- Excluir os nutrientes 7 (colesterol em g) e 10 (energia em kJ) e seus vínculos em `alimento_nutrientes`. Preservar as medições em mg e kcal, os demais nutrientes e as chaves estrangeiras da tabela de associação.
- Manter o Django, os esquemas SQL, o seed e a cópia de distribuição do SQLite compatíveis.
