# Modelo semântico

Todos os relacionamentos são `1:*`, com filtro unidirecional da dimensão para a fato.

| Dimensão | Coluna | Fato | Coluna | Ativo |
|---|---|---|---|---|
| dim_date | date_key | fact_sales | date_key | Sim |
| dim_customer | customer_key | fact_sales | customer_key | Sim |
| dim_product | product_key | fact_sales | product_key | Sim |
| dim_store | store_key | fact_sales | store_key | Sim |
| dim_channel | channel_key | fact_sales | channel_key | Sim |
| dim_promotion | promotion_key | fact_sales | promotion_key | Sim |
| dim_date | date_key | fact_inventory_snapshot | date_key | Sim |
| dim_product | product_key | fact_inventory_snapshot | product_key | Sim |
| dim_store | store_key | fact_inventory_snapshot | store_key | Sim |

## Formatação

- Moedas: `R$ #,##0;[Red]-R$ #,##0`
- Percentuais: `0.0%`
- Quantidades: `#,##0`
- Datas: `dd/mm/yyyy`

## Organização

- Ocultar todas as chaves técnicas.
- Separar medidas nas pastas `Financeiro`, `Clientes`, `Operações` e `Time Intelligence`.
- Configurar descrições para medidas e colunas de negócio.
- Desabilitar soma automática para chaves, anos e códigos.
- Usar `_Measures` como tabela inicial da lista de campos.
