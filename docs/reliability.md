# Confiabilidade operacional

## Falhas transitórias

A ingestão executa até três tentativas por padrão, com backoff exponencial de 1, 2 e no máximo 10 segundos. O número de tentativas pode ser configurado por `--max-attempts`.

Em produção, a função `retryable` deve ser restrita a erros transitórios do driver, como indisponibilidade de conexão. Erros de contrato, conversão ou integridade devem falhar imediatamente e exigir correção dos dados ou do código.

## Atomicidade

Cada execução de banco usa uma transação. Uma falha impede a publicação parcial em staging. O status final, as contagens e a mensagem de erro são registrados em `raw.ingestion_runs`.

## Observabilidade

- Logs estruturados são enviados para a saída padrão.
- Cada execução recebe um UUID.
- Registros brutos preservam origem, número da linha, hash e horário.
- Rejeições preservam payload e códigos de erro.
- O relatório de qualidade separa causa original de impacto propagado.

## Política sugerida

| Situação | Comportamento |
|---|---|
| Banco temporariamente indisponível | Retry com backoff |
| CSV ausente | Falha imediata |
| Registro inválido | Quarentena da linha e dependentes |
| Falha inesperada durante a transação | Rollback e execução marcada como falha |
| Reexecução do mesmo arquivo | Nenhuma duplicação devido ao hash |
