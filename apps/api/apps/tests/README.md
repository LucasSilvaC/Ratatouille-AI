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

Para um endpoint novo, comece com `APITestCase` e chame sua URL usando `self.client`. Teste o resultado que o consumidor pode observar, como status e campos retornados. Use `force_authenticate` quando o teste avalia a permissão ou a operação do recurso. Para testar JWT, obtenha um token pela rota e envie o cabeçalho real.
