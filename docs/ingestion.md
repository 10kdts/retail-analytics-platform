# Ingestão raw → staging

## Funcionamento

1. Lê as sete fontes CSV na ordem de dependência.
2. Calcula SHA-256 sobre a representação canônica de cada linha.
3. Aplica regras de domínio, obrigatoriedade e integridade referencial.
4. Persiste a cópia original como JSONB em `raw.source_records`.
5. Envia registros inválidos para `raw.rejections`.
6. Converte e faz upsert dos registros válidos nas tabelas tipadas de `staging`.
7. Registra contagens e status em `raw.ingestion_runs`.

## Idempotência e incrementalidade

A restrição `(source_name, row_hash)` evita duplicação da mesma versão de uma linha. Uma linha alterada recebe outro hash, permanece rastreável na camada raw e atualiza a chave de negócio correspondente em staging.

## Propagação de qualidade

A primeira ocorrência de um e-mail é preservada e ocorrências posteriores são rejeitadas. Quando um registro pai é enviado à quarentena, os filhos dependentes também são rejeitados: pedidos de clientes inválidos e itens de pedidos inválidos não chegam a staging. Isso garante que a carga respeite todas as chaves estrangeiras e torna explícito o impacto de uma falha de qualidade ao longo do pipeline.
