# Testes da API

Os módulos `test_*.py` são descobertos pelo executor de testes do Django. Ele cria
e remove uma base PostgreSQL separada. Use uma credencial com `CREATEDB` em uma
instância de desenvolvimento descartável e configure a conexão pelas variáveis
`DJANGO_DB_*` do [guia de infraestrutura](../../../../infra/README.md).

Configure também `DJANGO_RESPONSE_KMS_KEY_ID` e `DJANGO_RESPONSE_PUBLIC_KEY`
com uma chave RSA descartável para os testes de gravação. A API precisa apenas
da parte pública. O teste do adaptador interno usa sua própria chave local
para simular o AWS KMS.

Execute a suíte ou um módulo específico a partir da raiz.

```powershell
node infra/scripts/with-env.mjs apps/api/env/Scripts/python.exe apps/api/manage.py test apps.tests
node infra/scripts/with-env.mjs apps/api/env/Scripts/python.exe apps/api/manage.py test apps.tests.test_filters
```

- `test_models.py` verifica regras do ORM e restrições SQL.
- `test_foods.py`, `test_diagnosis.py` e `test_accounts.py` verificam os contratos HTTP, incluindo validação, autorização e exclusões protegidas.
- `test_filters.py` verifica filtros combinados e a separação entre respostas de autores diferentes.
- `test_password_recovery.py` testa o e-mail com o backend em memória, segue o link gerado e verifica a invalidação de tokens antigos.

## Cenários de segurança do piloto

| Cenário                                                                    | Validação                                                                   |
| -------------------------------------------------------------------------- | --------------------------------------------------------------------------- |
| Requisição anônima, JWT expirado e limites de conta                        | `test_api_errors.py`, `test_access_protection.py`                           |
| Titular, outro usuário e staff em contas, catálogo e respostas             | `test_accounts.py`, `test_foods.py`, `test_diagnosis.py`, `test_privacy.py` |
| Cadastro fechado, provisionamento, e-mail confirmado e recuperação         | `test_pilot_accounts.py`, `test_password_recovery.py`                       |
| Campos inválidos, erros seguros e preservação do cabeçalho de autenticação | `test_api_errors.py` e testes de contrato por recurso                       |
| Correlação e metadados permitidos na auditoria                             | `test_audit.py`, `test_safe_logging.py`                                     |
| Respostas cifradas e acesso interno limitado ao escopo                     | `test_response_encryption.py`                                               |
| Inicialização do modo público e rejeição de configurações inseguras        | `test_deployment_settings.py`                                               |

`test_privacy.py` usa JWTs reais para verificar leitura, listagem filtrada,
alteração e exclusão entre contas comuns e staff. Também verifica as
diretivas `private` e `no-store` em respostas com dados de conta ou metadados
do questionário respondido.

`test_api_errors.py` cobre JSON inválido e a sanitização de erros construídos
fora do handler central. `test_audit.py` verifica a correlação de falhas
de banco e SMTP. `test_safe_logging.py` verifica que os campos permitidos
não carregam valores privados ou códigos fora da lista.

No ambiente do piloto, confira HTTPS e isolamento da porta da API, siga um
link de recuperação usando uma conta de teste e confirme que o proxy não
registra o link. Compare o `X-Request-ID` de uma resposta da API com o evento
correspondente no Django e com o registro do proxy, quando habilitado.

Para um endpoint novo, comece com `APITestCase` e chame sua URL usando `self.client`. Teste o resultado que o consumidor pode observar, como status e campos retornados. Use `force_authenticate` quando o teste avalia a permissão ou a operação do recurso. Para testar JWT, obtenha um token pela rota e envie o cabeçalho real.
