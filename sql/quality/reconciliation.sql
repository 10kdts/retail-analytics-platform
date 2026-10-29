-- Deve retornar diferença zero para todas as medidas após a carga dos marts.
WITH staging_totals AS (
    SELECT
        sum(item.quantity * item.unit_price) AS gross_revenue,
        sum(item.discount_amount) AS discount_amount,
        sum(item.quantity * item.unit_price - item.discount_amount) AS net_revenue,
        sum(item.quantity * item.unit_cost) AS cost_of_goods
    FROM staging.order_items AS item
    JOIN staging.orders AS sale ON sale.order_id = item.order_id
), mart_totals AS (
    SELECT
        sum(gross_revenue) AS gross_revenue,
        sum(discount_amount) AS discount_amount,
        sum(net_revenue) AS net_revenue,
        sum(cost_of_goods) AS cost_of_goods
    FROM marts.fact_sales
)
SELECT
    mart.gross_revenue - staging.gross_revenue AS gross_revenue_difference,
    mart.discount_amount - staging.discount_amount AS discount_difference,
    mart.net_revenue - staging.net_revenue AS net_revenue_difference,
    mart.cost_of_goods - staging.cost_of_goods AS cost_difference
FROM staging_totals AS staging CROSS JOIN mart_totals AS mart;
