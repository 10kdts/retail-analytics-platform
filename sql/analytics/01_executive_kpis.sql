-- Visão executiva mensal com crescimento, ticket e margem.
WITH monthly AS (
    SELECT
        date_trunc('month', order_date)::date AS month,
        count(DISTINCT order_id) AS orders,
        count(DISTINCT customer_id) AS active_customers,
        sum(net_revenue) AS net_revenue,
        sum(gross_margin) AS gross_margin
    FROM marts.vw_sales
    WHERE order_status = 'Completed'
    GROUP BY 1
)
SELECT
    month, orders, active_customers, net_revenue, gross_margin,
    net_revenue / NULLIF(orders, 0) AS average_order_value,
    gross_margin / NULLIF(net_revenue, 0) AS margin_rate,
    net_revenue / NULLIF(lag(net_revenue) OVER (ORDER BY month), 0) - 1 AS month_over_month_growth,
    net_revenue / NULLIF(lag(net_revenue, 12) OVER (ORDER BY month), 0) - 1 AS year_over_year_growth
FROM monthly
ORDER BY month;
