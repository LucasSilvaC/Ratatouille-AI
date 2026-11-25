# API Django do RatatouilleAI

Esta API fornece autenticação, catálogo alimentar, perguntas e respostas pelo
Django REST Framework (DRF). O ORM do Django administra o esquema no PostgreSQL
e integra os modelos aos serializers, à autenticação e ao Django Admin.

## Começar

Para executar a API inteira no Docker, use `pnpm infra:up api`. Para executar o
Django na máquina com o PostgreSQL do Compose, use Python 3.14 e execute pela raiz:

```powershell
python -m venv apps/api/env
apps/api/env/Scripts/python.exe -m pip install -r apps/api/requirements.txt
```

Para gravar respostas, configure o ARN e a chave pública em
`DJANGO_RESPONSE_KMS_KEY_ID` e `DJANGO_RESPONSE_PUBLIC_KEY`. Veja o
[guia de criptografia](../../infra/database/README.md#criptografia-das-respostas)
para migrar dados de uma instalação existente.

```powershell
pnpm infra:db api-db-init
node infra/scripts/with-env.mjs docker compose --project-directory infra --file infra/compose.yaml wait api-db-init
node infra/scripts/with-env.mjs apps/api/env/Scripts/python.exe apps/api/manage.py migrate
node infra/scripts/with-env.mjs apps/api/env/Scripts/python.exe apps/api/manage.py seed_catalog
node infra/scripts/with-env.mjs apps/api/env/Scripts/python.exe apps/api/manage.py runserver
```

`api-db-init` provisiona a base e a credencial da API no PostgreSQL local.
`migrate` cria as tabelas e aplica as migrações pendentes nessa base.
`seed_catalog` carrega o catálogo inicial quando as quatro tabelas do catálogo estão
vazias. Se alguma já tiver registros, o comando preserva o catálogo existente.
Veja a [referência do banco e do seed](../../infra/database/README.md).

- [Swagger](http://127.0.0.1:8000/api/swagger/) para ver e testar os endpoints.
- [Esquema OpenAPI](http://127.0.0.1:8000/api/schema/) para consultar o contrato em formato estruturado.
- [Django Admin](http://127.0.0.1:8000/admin/) no modo local. Crie uma conta local com `node infra/scripts/with-env.mjs apps/api/env/Scripts/python.exe apps/api/manage.py createsuperuser`.

No Swagger, envie `username` e `password` para `POST /api/token/`. Cole o valor de `access` em **Authorize**. O Swagger adiciona o prefixo `Bearer`; em um cliente HTTP próprio, envie `Authorization: Bearer <access>`. Use `POST /api/token/refresh/` com o valor de `refresh` para renovar o acesso.

Novos tokens de acesso duram 15 minutos e o token de renovação dura um dia.
Login, cadastro e renovação retornam HTTP `429` com `Retry-After` quando o
limite por IP é atingido. Veja o [guia de HTTPS e limites](../../infra/README.md#publicar-por-https).

## Onde a requisição passa

1. [project/urls.py](project/urls.py) encaminha os caminhos que começam com `/api/` para [apps/urls.py](apps/urls.py). Esse segundo arquivo liga cada caminho à sua view e define seu nome para uso com `reverse()`.
2. A **view** executa a operação HTTP. Por exemplo, `ListCreateAPIView` implementa `GET` para listar e `POST` para criar. A view declara quais permissões se aplicam e qual conjunto de registros pode ser consultado.
3. O DRF lê o JSON recebido e entrega dados Python ao **serializer**, que os valida antes de salvar. Na saída, o serializer converte os registros em valores simples que o DRF pode renderizar como JSON.
4. O **modelo** representa a tabela no ORM. Métodos como `Alimento.objects.filter(...)` montam uma consulta, e o Django gera o SQL ao avaliar o resultado. Restrições e relações também podem ser impostas diretamente pelo banco.

Views de listagem aplicam filtros ao conjunto autorizado e só então paginam os resultados. As listas paginadas devolvem `count`, `next`, `previous` e `results`.

## Onde fazer alterações

| Caminho                                                                                                 | Responsabilidade                                                                                                                                   |
| ------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------- |
| [accounts/](apps/accounts/)                                                                             | Cadastro, perfil, exclusão de conta e senhas. A equipe pode consultar apenas o ID e o nome de usuário de outras contas.                            |
| [foods/](apps/foods/)                                                                                   | Classes, alimentos, nutrientes e medições. `filters.py` descreve filtros de listagem que também aparecem no Swagger.                               |
| [diagnosis/](apps/diagnosis/)                                                                           | Perguntas com opções ou texto livre explícito. Somente o autor acessa suas respostas.                                                              |
| [models.py](apps/models.py)                                                                             | Modelos compartilhados. `User` amplia o usuário do Django e usa a tabela `auth_user`.                                                              |
| [permissions.py](apps/permissions.py), [pagination.py](apps/pagination.py), [mixins.py](apps/mixins.py) | Regras reutilizadas. Catálogo e perguntas permitem leitura autenticada e escrita por staff. Uma exclusão bloqueada por vínculo retorna HTTP `409`. |
| [templates/api/](apps/templates/api/)                                                                   | Assunto e corpo do e-mail de recuperação e páginas de confirmação servidas pelo Django. A entrega real usa SMTP.                                   |
| [migrations/](apps/migrations/README.md) e [tests/](apps/tests/README.md)                               | Histórico do banco e testes automatizados.                                                                                                         |

Por exemplo, `GET /api/alimentos/?descricao=banana&classe=8` combina a busca por trecho de descrição e o ID da classe. Use `search` para buscar pelo código, pela descrição ou pelo nome da classe no mesmo parâmetro.

A configuração de ambiente e SMTP fica em [infra/README.md](../../infra/README.md). Use uma `DJANGO_SECRET_KEY` estável no ambiente do processo para manter JWTs, sessões e links de recuperação válidos entre reinícios.

O titular pode excluir a conta com `DELETE /api/usuarios/<id>/`. A operação
remove o perfil, as respostas associadas e os registros dos tokens de renovação.
No Admin local, só superusuários administram contas, e o formulário não exibe
campos do perfil alimentar. Veja a
[regras de coleta e acesso](../../infra/database/README.md#coleta-e-acesso).

O Django cifra as respostas antes de gravar e retorna apenas metadados
ao titular autenticado, inclusive após envio ou edição. O titular pode
substituir ou excluir uma resposta e filtrar a listagem por `pergunta`.
