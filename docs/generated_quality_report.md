# Relatório de qualidade dos dados

- Linhas avaliadas: **5,157**
- Linhas válidas: **5,101**
- Linhas rejeitadas: **56**
- Taxa de validade: **98.91%**
- Anomalias documentadas detectadas: **5/5**
- Rejeições em cascata: **52**
- Contrato de qualidade: **PASSED**

## Qualidade por fonte

| Fonte | Linhas | Válidas | Rejeitadas | Taxa de validade |
|---|---:|---:|---:|---:|
| customers.csv | 120 | 118 | 2 | 98.33% |
| products.csv | 40 | 40 | 0 | 100.00% |
| stores.csv | 6 | 6 | 0 | 100.00% |
| promotions.csv | 6 | 6 | 0 | 100.00% |
| orders.csv | 600 | 584 | 16 | 97.33% |
| order_items.csv | 1,505 | 1,467 | 38 | 97.48% |
| inventory_snapshots.csv | 2,880 | 2,880 | 0 | 100.00% |

## Ocorrências por regra

| Regra | Ocorrências |
|---|---:|
| customer_fk | 15 |
| email_unique | 1 |
| order_fk | 37 |
| quantity_positive | 1 |
| state_not_null | 1 |
| valid_channel | 1 |

## Interpretação

As rejeições em cascata são intencionais: registros filhos não podem ser publicados quando o pai foi enviado à quarentena. A taxa de validade mede prontidão para staging, enquanto o contrato verifica se as falhas conhecidas foram detectadas corretamente.
