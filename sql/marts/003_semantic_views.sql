CREATE OR REPLACE VIEW marts.vw_sales AS
SELECT
    fact.order_item_id,
    fact.order_id,
    calendar.full_date AS order_date,
    calendar.year_number,
    calendar.month_number,
    customer.customer_id,
    customer.segment AS customer_segment,
    customer.state AS customer_state,
    product.product_id,
    product.product_name,
    product.category,
    product.brand,
    store.store_name,
    store.region AS store_region,
    channel.channel_name,
    promotion.promotion_name,
    fact.payment_method,
    fact.order_status,
    fact.quantity,
    fact.gross_revenue,
    fact.discount_amount,
    fact.net_revenue,
    fact.cost_of_goods,
    fact.gross_margin
FROM marts.fact_sales AS fact
JOIN marts.dim_date AS calendar ON calendar.date_key = fact.date_key
JOIN marts.dim_customer AS customer ON customer.customer_key = fact.customer_key
JOIN marts.dim_product AS product ON product.product_key = fact.product_key
LEFT JOIN marts.dim_store AS store ON store.store_key = fact.store_key
JOIN marts.dim_channel AS channel ON channel.channel_key = fact.channel_key
LEFT JOIN marts.dim_promotion AS promotion ON promotion.promotion_key = fact.promotion_key;

CREATE OR REPLACE VIEW marts.vw_monthly_sales AS
SELECT
    date_trunc('month', order_date)::date AS month,
    channel_name,
    category,
    count(DISTINCT order_id) FILTER (WHERE order_status = 'Completed') AS completed_orders,
    sum(quantity) FILTER (WHERE order_status = 'Completed') AS units_sold,
    sum(net_revenue) FILTER (WHERE order_status = 'Completed') AS net_revenue,
    sum(gross_margin) FILTER (WHERE order_status = 'Completed') AS gross_margin,
    sum(gross_margin) FILTER (WHERE order_status = 'Completed')
      / NULLIF(sum(net_revenue) FILTER (WHERE order_status = 'Completed'), 0) AS margin_rate
FROM marts.vw_sales
GROUP BY 1, 2, 3;

CREATE OR REPLACE VIEW marts.vw_inventory_risk AS
WITH monthly_demand AS (
    SELECT
        product_key,
        store_key,
        date_trunc('month', calendar.full_date)::date AS month,
        sum(quantity) FILTER (WHERE order_status = 'Completed') AS units_sold
    FROM marts.fact_sales AS sales
    JOIN marts.dim_date AS calendar ON calendar.date_key = sales.date_key
    GROUP BY 1, 2, 3
)
SELECT
    calendar.full_date AS snapshot_date,
    store.store_id,
    store.store_name,
    product.product_id,
    product.product_name,
    inventory.on_hand_quantity,
    inventory.reorder_point,
    inventory.lead_time_days,
    demand.units_sold,
    inventory.on_hand_quantity / NULLIF(demand.units_sold / 30.0, 0) AS coverage_days,
    CASE
      WHEN inventory.on_hand_quantity <= inventory.reorder_point THEN 'Repor agora'
      WHEN inventory.on_hand_quantity / NULLIF(demand.units_sold / 30.0, 0) < inventory.lead_time_days THEN 'Risco de ruptura'
      ELSE 'Saudável'
    END AS inventory_status
FROM marts.fact_inventory_snapshot AS inventory
JOIN marts.dim_date AS calendar ON calendar.date_key = inventory.date_key
JOIN marts.dim_store AS store ON store.store_key = inventory.store_key
JOIN marts.dim_product AS product ON product.product_key = inventory.product_key
LEFT JOIN monthly_demand AS demand
  ON demand.product_key = inventory.product_key
 AND demand.store_key = inventory.store_key
 AND demand.month = (calendar.full_date - INTERVAL '1 month')::date;
