# Plano de migração do usuário e código de alimento

1. Validar o limite de seis caracteres no modelo, na camada SQL e com o catálogo existente.
2. Introduzir o modelo de usuário na migração inicial para atender à dependência dinâmica de `AUTH_USER_MODEL` e registrar o modelo com `UserAdmin`.
3. Evoluir `auth_user`, preservar contas e relações existentes, migrar perfis e respostas em transação e excluir a tabela legada após verificar os vínculos.
4. Alinhar os esquemas e os dois SQLite. Testar banco vazio, atualização de base legada, autenticação, vínculos de respostas e rejeição de códigos com comprimento incorreto.
