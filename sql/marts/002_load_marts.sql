BEGIN;

INSERT INTO marts.dim_date (
    date_key, full_date, day_of_month, month_number, month_name,
    quarter_number, year_number, iso_week, day_of_week, day_name, is_weekend
)
SELECT
    to_char(d, 'YYYYMMDD')::integer,
    d::date,
    extract(day FROM d)::smallint,
    extract(month FROM d)::smallint,
    to_char(d, 'TMMonth'),
    extract(quarter FROM d)::smallint,
    extract(year FROM d)::smallint,
    extract(week FROM d)::smallint,
    extract(isodow FROM d)::smallint,
    to_char(d, 'TMDay'),
    extract(isodow FROM d) IN (6, 7)
FROM generate_series(DATE '2024-01-01', DATE '2026-12-31', INTERVAL '1 day') AS dates(d)
ON CONFLICT (date_key) DO NOTHING;

INSERT INTO marts.dim_channel(channel_name)
VALUES ('Loja física'), ('E-commerce'), ('Marketplace')
ON CONFLICT (channel_name) DO NOTHING;

INSERT INTO marts.dim_product(product_id, product_name, category, brand, active, source_hash)
SELECT product_id, product_name, category, brand, active, source_hash
FROM staging.products
ON CONFLICT (product_id) DO UPDATE SET
    product_name = EXCLUDED.product_name,
    category = EXCLUDED.category,
    brand = EXCLUDED.brand,
    active = EXCLUDED.active,
    source_hash = EXCLUDED.source_hash;

INSERT INTO marts.dim_store(store_id, store_name, city, state, region, opened_at, source_hash)
SELECT store_id, store_name, city, state, region, opened_at, source_hash
FROM staging.stores
ON CONFLICT (store_id) DO UPDATE SET
    store_name = EXCLUDED.store_name, city = EXCLUDED.city,
    state = EXCLUDED.state, region = EXCLUDED.region,
    opened_at = EXCLUDED.opened_at, source_hash = EXCLUDED.source_hash;

INSERT INTO marts.dim_promotion(promotion_id, promotion_name, start_date, end_date, discount_rate)
SELECT promotion_id, promotion_name, start_date, end_date, discount_rate
FROM staging.promotions
ON CONFLICT (promotion_id) DO UPDATE SET
    promotion_name = EXCLUDED.promotion_name, start_date = EXCLUDED.start_date,
    end_date = EXCLUDED.end_date, discount_rate = EXCLUDED.discount_rate;

-- SCD Tipo 2: encerra apenas versões cujo conjunto de atributos realmente mudou.
UPDATE marts.dim_customer AS target
SET valid_to = CURRENT_DATE - 1, is_current = false
FROM staging.customers AS source
WHERE target.customer_id = source.customer_id
  AND target.is_current
  AND target.source_hash <> source.source_hash;

INSERT INTO marts.dim_customer (
    customer_id, full_name, email, birth_year, city, state, segment,
    marketing_consent, valid_from, source_hash
)
SELECT
    source.customer_id, source.full_name, source.email, source.birth_year,
    source.city, source.state, source.segment, source.marketing_consent,
    CASE
      WHEN EXISTS (
        SELECT 1 FROM marts.dim_customer AS history
        WHERE history.customer_id = source.customer_id
      ) THEN CURRENT_DATE
      ELSE source.signup_date
    END,
    source.source_hash
FROM staging.customers AS source
LEFT JOIN marts.dim_customer AS current_version
    ON current_version.customer_id = source.customer_id AND current_version.is_current
WHERE current_version.customer_key IS NULL;

INSERT INTO marts.fact_sales (
    order_item_id, order_id, date_key, customer_key, product_key, store_key,
    channel_key, promotion_key, payment_method, order_status, quantity,
    unit_price, unit_cost, gross_revenue, discount_amount, net_revenue,
    cost_of_goods, gross_margin
)
SELECT
    item.order_item_id,
    sale.order_id,
    to_char(sale.order_date, 'YYYYMMDD')::integer,
    customer.customer_key,
    product.product_key,
    store.store_key,
    channel.channel_key,
    promotion.promotion_key,
    sale.payment_method,
    sale.status,
    item.quantity,
    item.unit_price,
    item.unit_cost,
    item.quantity * item.unit_price,
    item.discount_amount,
    item.quantity * item.unit_price - item.discount_amount,
    item.quantity * item.unit_cost,
    item.quantity * item.unit_price - item.discount_amount - item.quantity * item.unit_cost
FROM staging.order_items AS item
JOIN staging.orders AS sale ON sale.order_id = item.order_id
JOIN marts.dim_customer AS customer
  ON customer.customer_id = sale.customer_id
 AND sale.order_date BETWEEN customer.valid_from AND customer.valid_to
JOIN marts.dim_product AS product ON product.product_id = item.product_id
LEFT JOIN marts.dim_store AS store ON store.store_id = sale.store_id
JOIN marts.dim_channel AS channel ON channel.channel_name = sale.channel
LEFT JOIN marts.dim_promotion AS promotion ON promotion.promotion_id = item.promotion_id
ON CONFLICT (order_item_id) DO UPDATE SET
    order_id = EXCLUDED.order_id, date_key = EXCLUDED.date_key,
    customer_key = EXCLUDED.customer_key, product_key = EXCLUDED.product_key,
    store_key = EXCLUDED.store_key, channel_key = EXCLUDED.channel_key,
    promotion_key = EXCLUDED.promotion_key, payment_method = EXCLUDED.payment_method,
    order_status = EXCLUDED.order_status, quantity = EXCLUDED.quantity,
    unit_price = EXCLUDED.unit_price, unit_cost = EXCLUDED.unit_cost,
    gross_revenue = EXCLUDED.gross_revenue, discount_amount = EXCLUDED.discount_amount,
    net_revenue = EXCLUDED.net_revenue, cost_of_goods = EXCLUDED.cost_of_goods,
    gross_margin = EXCLUDED.gross_margin, loaded_at = now();

INSERT INTO marts.fact_inventory_snapshot (
    date_key, store_key, product_key, on_hand_quantity, reorder_point, lead_time_days
)
SELECT
    to_char(snapshot.snapshot_date, 'YYYYMMDD')::integer,
    store.store_key,
    product.product_key,
    snapshot.on_hand_quantity,
    snapshot.reorder_point,
    snapshot.lead_time_days
FROM staging.inventory_snapshots AS snapshot
JOIN marts.dim_store AS store ON store.store_id = snapshot.store_id
JOIN marts.dim_product AS product ON product.product_id = snapshot.product_id
ON CONFLICT (date_key, store_key, product_key) DO UPDATE SET
    on_hand_quantity = EXCLUDED.on_hand_quantity,
    reorder_point = EXCLUDED.reorder_point,
    lead_time_days = EXCLUDED.lead_time_days,
    loaded_at = now();

COMMIT;
