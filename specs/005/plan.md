# Plano de segurança do piloto

1. Fortalecer o deploy público nas configurações existentes e documentar o proxy.
2. Aplicar permissão padrão no DRF e limitar a documentação interativa ao ambiente local.
3. Fechar o cadastro público e provisionar participantes por operação, reaproveitando a recuperação de senha.
4. Registrar eventos por rota e método com ID gerado no Django. Capturar o mesmo ID no proxy.
5. Normalizar erros do DRF e do Django na fronteira HTTP. Validar por testes de contrato e regressão da API.
