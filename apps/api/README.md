# API Django do RatatouilleAI

Esta API fornece autenticação, catálogo alimentar, perguntas e respostas pelo Django REST Framework (DRF). Ela usa SQLite no desenvolvimento local.

## Começar

Execute os comandos abaixo na raiz do repositório, com Python 3.14.

```powershell
python -m venv apps/api/env
apps/api/env/Scripts/python.exe -m pip install -r apps/api/requirements.txt
if (-not (Test-Path apps/api/db.sqlite)) {
    Copy-Item infra/database/db.sqlite apps/api/db.sqlite
}
apps/api/env/Scripts/python.exe apps/api/manage.py migrate
apps/api/env/Scripts/python.exe apps/api/manage.py runserver
```

Copiar o SQLite de distribuição disponibiliza o catálogo no primeiro uso. Se o arquivo local já existe, o comando de cópia é pulado para preservar os dados locais. `migrate` aplica as alterações de banco pendentes.

- [Swagger](http://127.0.0.1:8000/api/swagger/) para ver e testar os endpoints.
- [Esquema OpenAPI](http://127.0.0.1:8000/api/schema/) para consultar o contrato em formato estruturado.
- [Django Admin](http://127.0.0.1:8000/admin/) para administração. Crie uma conta local com `apps/api/env/Scripts/python.exe apps/api/manage.py createsuperuser`.

No Swagger, envie `username` e `password` para `POST /api/token/`. Cole o valor de `access` em **Authorize**. O Swagger adiciona o prefixo `Bearer`; em um cliente HTTP próprio, envie `Authorization: Bearer <access>`. Use `POST /api/token/refresh/` com o valor de `refresh` para renovar o acesso.

## Onde a requisição passa

1. [project/urls.py](project/urls.py) encaminha os caminhos que começam com `/api/` para [apps/api/urls.py](apps/api/urls.py). Esse segundo arquivo liga cada caminho à sua view e define seu nome para uso com `reverse()`.
2. A **view** executa a operação HTTP. Por exemplo, `ListCreateAPIView` implementa `GET` para listar e `POST` para criar. A view declara quais permissões se aplicam e qual conjunto de registros pode ser consultado.
3. O DRF lê o JSON recebido e entrega dados Python ao **serializer**, que os valida antes de salvar. Na saída, o serializer converte os registros em valores simples que o DRF pode renderizar como JSON.
4. O **modelo** representa a tabela no ORM. Métodos como `Alimento.objects.filter(...)` montam uma consulta, e o Django gera o SQL ao avaliar o resultado. Restrições e relações também podem ser impostas diretamente pelo banco.

Views de listagem aplicam filtros ao conjunto autorizado e só então paginam os resultados. As listas paginadas devolvem `count`, `next`, `previous` e `results`.

## Onde fazer alterações

| Caminho                                                                                                             | Responsabilidade                                                                                                                                    |
| ------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------- |
| [accounts/](apps/api/accounts/)                                                                                     | Cadastro, perfil e senhas. A troca autenticada e a confirmação por e-mail usam a mesma operação para atualizar a senha e revogar tokens anteriores. |
| [catalog/](apps/api/catalog/)                                                                                       | Classes, alimentos, nutrientes e medições. `filters.py` descreve filtros de listagem que também aparecem no Swagger.                                |
| [questionnaire/](apps/api/questionnaire/)                                                                           | Perguntas e respostas. As respostas ficam restritas ao próprio autor, inclusive quando outro usuário faz parte da equipe.                           |
| [models.py](apps/api/models.py)                                                                                     | Modelos compartilhados. `User` amplia o usuário do Django e usa a tabela `auth_user`.                                                               |
| [permissions.py](apps/api/permissions.py), [pagination.py](apps/api/pagination.py), [mixins.py](apps/api/mixins.py) | Regras reutilizadas. Catálogo e perguntas permitem leitura autenticada e escrita por staff. Uma exclusão bloqueada por vínculo retorna HTTP `409`.  |
| [templates/api/](apps/api/templates/api/)                                                                           | Assunto e corpo do e-mail de recuperação e páginas de confirmação servidas pelo Django. A entrega real usa SMTP.                                    |
| [migrations/](apps/api/migrations/README.md) e [tests/](apps/api/tests/README.md)                                   | Histórico do banco e testes automatizados.                                                                                                          |

Por exemplo, `GET /api/alimentos/?descricao=banana&classe=8` combina a busca por trecho de descrição e o ID da classe. Use `search` para buscar pelo código, pela descrição ou pelo nome da classe no mesmo parâmetro.

A configuração de ambiente e SMTP fica em [infra/README.md](../../infra/README.md). Use uma `DJANGO_SECRET_KEY` estável no ambiente do processo para manter JWTs, sessões e links de recuperação válidos entre reinícios.
