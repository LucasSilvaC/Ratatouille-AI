# Plano de entrega dos CRUDs

1. Cobrir cada recurso com uma fatia TDD pela rota HTTP, começando pela autenticação e pelas fronteiras de autorização.
2. Implementar serializers, views e URLs nomeadas. Usar paginação estável para listas e proteger a autoria das respostas.
3. Testar tokens, senhas, CRUD e casos de acesso indevido, vínculos inválidos e exclusões protegidas.
4. Executar a suíte Django, a checagem de migrações e a resolução das rotas montadas em `/api/`.
