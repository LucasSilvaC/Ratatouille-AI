# Segurança da API no piloto

O piloto com dados reais usa contas provisionadas e e-mails confirmados pela operação. O ambiente local mantém cadastro aberto para demonstração. As rotas de negócio exigem autenticação por padrão e preservam as regras de titularidade e staff.

Erros HTTP em `/api/` têm código, mensagem segura e ID de requisição. Validações identificam os campos e seus códigos. Respostas de erro preservam o status e os cabeçalhos de autenticação e throttling. O mesmo ID aparece no cabeçalho de resposta e nos eventos de auditoria relevantes. A trilha exclui credenciais e dados alimentares.

O deploy público exige parâmetros seguros e um proxy HTTPS. A validação cobre permissões, provisionamento, recuperação, falhas sanitizadas, correlação e configuração. A revisão do proxy instalado fica com o ambiente de publicação.
