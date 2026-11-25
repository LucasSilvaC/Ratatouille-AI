# Worker de IA

Futura aplicação Python para tarefas demoradas de geração e jobs de treinamento. Importa agents, recommendation e neural. Planejar fila, timeout, progresso persistido, tentativas limitadas e idempotência. Treinamento deve ter fila e recursos separados da geração quando necessário. Não existe consumidor ou broker configurado.

Status: estrutura planejada; sem implementação nesta etapa.

## Respostas do questionário

O adaptador interno `apps.diagnosis.agent_responses.read_job_answers` já está disponível
no código Django. O worker deverá chamar o adaptador após validar a origem da
tarefa, seu titular e os IDs de respostas necessários. Passe um cliente AWS KMS
da identidade do worker e uma lista de ARNs permitidos. Conceda `kms:Decrypt`
apenas a essa identidade e apenas para essas chaves. Use uma credencial de banco
própria, com leitura das colunas necessárias da tabela `respostas`.

Use o texto em memória para extrair o mínimo necessário para a tarefa. Envie
aos agentes e provedores somente os dados necessários, como as restrições
estruturadas. A API pública não encaminha JWTs ao adaptador nem expõe uma rota
de decifragem. Consulte o [guia de criptografia](../../infra/database/README.md#criptografia-das-respostas).
