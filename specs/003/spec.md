# Código de alimento e usuário do Django

- Exigir exatamente seis caracteres em `Alimento.codigo`.
- Consolidar a autenticação e os campos de perfil em um modelo `User` que herda de `AbstractUser` e usa a tabela `auth_user`.
- Preservar os campos `nome`, `idade`, `genero`, `peso`, `altura` e `disposicao`. Usar o campo Django `password` para credenciais.
- Fazer `respostas.usuario_id` referenciar o usuário configurado em `AUTH_USER_MODEL`.

A consolidação foi aprovada. Para bases legadas, a migração usa o UUID anterior como `username`, mantém hashes reconhecidos e marca as demais senhas como inutilizáveis até redefinição.
