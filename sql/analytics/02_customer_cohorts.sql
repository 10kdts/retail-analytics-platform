-- Retenção mensal por coorte da primeira compra concluída.
WITH purchases AS (
    SELECT DISTINCT customer_id, order_id, date_trunc('month', order_date)::date AS purchase_month
    FROM marts.vw_sales
    WHERE order_status = 'Completed'
), cohorts AS (
    SELECT customer_id, min(purchase_month) AS cohort_month
    FROM purchases GROUP BY customer_id
), activity AS (
    SELECT
        cohorts.cohort_month,
        purchases.purchase_month,
        (extract(year FROM age(purchases.purchase_month, cohorts.cohort_month)) * 12
          + extract(month FROM age(purchases.purchase_month, cohorts.cohort_month)))::integer AS month_number,
        count(DISTINCT purchases.customer_id) AS active_customers
    FROM purchases JOIN cohorts USING (customer_id)
    GROUP BY 1, 2, 3
)
SELECT
    cohort_month, purchase_month, month_number, active_customers,
    active_customers::numeric
      / NULLIF(first_value(active_customers) OVER (PARTITION BY cohort_month ORDER BY month_number), 0) AS retention_rate
FROM activity
ORDER BY cohort_month, month_number;
