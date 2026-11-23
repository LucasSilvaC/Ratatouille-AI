# Testes da API

Os módulos `test_*.py` são descobertos pelo executor de testes do Django. Ele cria um banco de teste separado. A base local usada pela API fica disponível para desenvolvimento.

Execute a suíte ou um módulo específico a partir da raiz.

```powershell
apps/api/env/Scripts/python.exe apps/api/manage.py test apps.api
apps/api/env/Scripts/python.exe apps/api/manage.py test apps.api.tests.test_filters
```

- `test_models.py` verifica regras do ORM e restrições SQL.
- `test_catalog.py`, `test_questionnaire.py` e `test_accounts.py` verificam os contratos HTTP, incluindo validação, autorização e exclusões protegidas.
- `test_filters.py` verifica filtros combinados e a separação entre respostas de autores diferentes.
- `test_password_recovery.py` testa o e-mail com o backend em memória, segue o link gerado e verifica a invalidação de tokens antigos.

Para um endpoint novo, comece com `APITestCase` e chame sua URL usando `self.client`. Teste o resultado que o consumidor pode observar, como status e campos retornados. Use `force_authenticate` quando o teste avalia a permissão ou a operação do recurso. Para testar JWT, obtenha um token pela rota e envie o cabeçalho real.
