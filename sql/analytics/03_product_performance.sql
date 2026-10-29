-- Ranking de produtos com participação acumulada (curva ABC).
WITH product_sales AS (
    SELECT product_id, product_name, category, sum(net_revenue) AS revenue, sum(gross_margin) AS margin
    FROM marts.vw_sales
    WHERE order_status = 'Completed'
    GROUP BY 1, 2, 3
), ranked AS (
    SELECT *,
        sum(revenue) OVER (ORDER BY revenue DESC)
          / NULLIF(sum(revenue) OVER (), 0) AS cumulative_revenue_share
    FROM product_sales
)
SELECT *,
    CASE WHEN cumulative_revenue_share <= 0.80 THEN 'A'
         WHEN cumulative_revenue_share <= 0.95 THEN 'B'
         ELSE 'C' END AS abc_class
FROM ranked
ORDER BY revenue DESC;
