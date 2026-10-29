# Resumo para apresentação

## Pitch de 30 segundos

O Retail Analytics é uma plataforma de dados de varejo construída de ponta a ponta. Ela gera dados sintéticos, ingere de forma incremental em PostgreSQL, aplica regras de qualidade com quarentena, publica um modelo dimensional e entrega uma camada semântica para Power BI. O projeto inclui testes, CI/CD, observabilidade, segurança e documentação operacional.

## Problema resolvido

Lideranças comerciais precisam acompanhar receita, margem, retenção e estoque sem depender de planilhas inconsistentes. A solução centraliza regras, preserva rastreabilidade e transforma dados operacionais em indicadores confiáveis.

## Decisões que demonstram senioridade

- Preservação imutável da entrada em raw.
- Idempotência baseada em hash.
- Propagação de quarentena para impedir filhos sem pais válidos.
- Histórico de clientes por SCD Tipo 2.
- Reconciliação entre staging e fatos.
- Métricas operacionais, retry, rollback e runbook.
- Segurança por RLS, permissões mínimas e análise automatizada.

## Resultados demonstráveis

- 5.157 registros avaliados.
- 98,22% de validade antes da publicação em staging.
- 5 de 5 anomalias controladas detectadas.
- 88 rejeições em cascata rastreadas.
- 20 testes unitários e de contrato aprovados localmente.
- Integração completa com PostgreSQL definida no GitHub Actions.

## Limitações honestas

- Os dados são sintéticos e não representam uma empresa real.
- O arquivo `.pbix` depende do Power BI Desktop.
- A integração PostgreSQL local depende de Docker, indisponível durante a construção.
- O cenário usa volume reduzido; decisões de particionamento e processamento distribuído exigiriam testes adicionais.

## Próximas evoluções possíveis

- Migrar para BigQuery, Snowflake ou Databricks.
- Adicionar dbt e catálogo de dados.
- Publicar telemetria em Prometheus/Grafana.
- Implementar previsão de demanda e monitoramento de modelo.
