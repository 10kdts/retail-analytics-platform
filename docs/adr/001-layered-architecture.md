# ADR 001 — Arquitetura em camadas

- Status: aceito
- Data: 2026-10-29

## Contexto

O projeto precisa demonstrar análise e engenharia sem depender de serviços cloud pagos. Também deve permitir auditoria, reprocessamento e evolução futura.

## Decisão

Adotar PostgreSQL com schemas `raw`, `staging` e `marts`. Raw preserva o evento recebido; staging contém registros válidos e tipados; marts oferece fatos, dimensões e visões semânticas.

## Consequências

- A origem de cada resultado pode ser rastreada.
- Reprocessamentos são idempotentes.
- A solução pode migrar para um warehouse cloud mantendo o desenho lógico.
- Há mais estruturas e documentação que em um notebook isolado, mas isso representa melhor um ambiente corporativo.
