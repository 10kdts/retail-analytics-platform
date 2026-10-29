# Dicionário de dados das fontes

Todos os arquivos usam CSV com cabeçalho, codificação UTF-8 com BOM e datas no padrão ISO `YYYY-MM-DD`.

## customers.csv

| Campo | Tipo lógico | Regra |
|---|---|---|
| customer_id | texto | Chave natural única e obrigatória |
| full_name | texto | Nome sintético |
| email | texto | Único; domínio `example.com` |
| birth_year | inteiro | Entre 1958 e 2004 na versão inicial |
| city | texto | Cidade de residência |
| state | texto | UF com dois caracteres |
| signup_date | data | Data de cadastro |
| segment | texto | Consumer, Premium ou Small Business |
| marketing_consent | booleano | `true` ou `false` |

## products.csv

| Campo | Tipo lógico | Regra |
|---|---|---|
| product_id | texto | Chave natural única |
| product_name | texto | Nome sintético |
| category | texto | Eletrônicos, Casa, Esporte ou Papelaria |
| brand | texto | Marca sintética |
| unit_cost | decimal(12,2) | Maior que zero |
| list_price | decimal(12,2) | Maior ou igual ao custo na geração padrão |
| active | booleano | Produto disponível no catálogo |

## stores.csv

| Campo | Tipo lógico | Regra |
|---|---|---|
| store_id | texto | Chave natural única |
| store_name | texto | Nome da unidade |
| city | texto | Cidade da unidade |
| state | texto | UF |
| region | texto | Região brasileira |
| opened_at | data | Data de abertura |

## promotions.csv

| Campo | Tipo lógico | Regra |
|---|---|---|
| promotion_id | texto | Chave natural única |
| promotion_name | texto | Nome da campanha |
| start_date | data | Início da vigência |
| end_date | data | Fim da vigência, não anterior ao início |
| discount_rate | decimal(5,4) | Entre zero e um |

## orders.csv

| Campo | Tipo lógico | Regra |
|---|---|---|
| order_id | texto | Chave natural única |
| customer_id | texto | FK para clientes |
| store_id | texto | FK opcional; obrigatória em loja física |
| order_date | data | Entre 2024-01-01 e 2025-12-31 |
| channel | texto | Loja física, E-commerce ou Marketplace |
| payment_method | texto | Cartão, Pix ou Boleto |
| status | texto | Completed, Cancelled ou Returned |

## order_items.csv

| Campo | Tipo lógico | Regra |
|---|---|---|
| order_item_id | texto | Chave única da linha |
| order_id | texto | FK para pedidos |
| product_id | texto | FK para produtos |
| quantity | inteiro | Maior que zero |
| unit_price | decimal(12,2) | Preço no momento da venda |
| unit_cost | decimal(12,2) | Custo no momento da venda |
| discount_amount | decimal(12,2) | Maior ou igual a zero |
| promotion_id | texto | FK opcional para promoções |

## inventory_snapshots.csv

| Campo | Tipo lógico | Regra |
|---|---|---|
| snapshot_date | data | Primeiro dia do mês |
| store_id | texto | FK para lojas |
| product_id | texto | FK para produtos |
| on_hand_quantity | inteiro | Maior ou igual a zero |
| reorder_point | inteiro | Ponto de reposição |
| lead_time_days | inteiro | Prazo estimado de reposição |

## expected_quality_issues.csv

Contrato de teste das anomalias intencionais. Não é uma fonte operacional e será utilizado para verificar se a camada de qualidade detecta todos os casos conhecidos.
