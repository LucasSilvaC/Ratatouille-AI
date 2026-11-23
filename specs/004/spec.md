# CRUD da API Django

- Publicar rotas nomeadas sob `/api/`, com views genéricas do Django REST Framework e serializers de campos explícitos.
- Oferecer lista, criação, detalhe, atualização e exclusão para classes, alimentos, nutrientes, medições, perguntas e respostas.
- Exigir autenticação para leitura de catálogo e perguntas. Restringir suas escritas a staff.
- Restringir todo acesso a respostas ao próprio autor. Definir a autoria no servidor e manter chaves primárias estáveis.
- Permitir cadastro e tokens JWT, além de consulta, atualização e exclusão do próprio perfil. Permitir listagem administrativa de usuários sem devolver credenciais ou campos de autorização.
- Responder com erro de validação para entradas inválidas, 404 para objetos fora do escopo e 409 para exclusões protegidas.

As permissões foram aprovadas. `redefinir_senha/` inicia a recuperação por
e-mail e o link leva à confirmação nativa do Django. A troca autenticada fica
em `senha/`.
