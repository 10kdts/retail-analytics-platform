CREATE TABLE IF NOT EXISTS marts.dim_date (
    date_key integer PRIMARY KEY,
    full_date date NOT NULL UNIQUE,
    day_of_month smallint NOT NULL,
    month_number smallint NOT NULL,
    month_name text NOT NULL,
    quarter_number smallint NOT NULL,
    year_number smallint NOT NULL,
    iso_week smallint NOT NULL,
    day_of_week smallint NOT NULL,
    day_name text NOT NULL,
    is_weekend boolean NOT NULL
);

CREATE TABLE IF NOT EXISTS marts.dim_customer (
    customer_key bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    customer_id text NOT NULL,
    full_name text NOT NULL,
    email text NOT NULL,
    birth_year smallint NOT NULL,
    city text NOT NULL,
    state char(2) NOT NULL,
    segment text NOT NULL,
    marketing_consent boolean NOT NULL,
    valid_from date NOT NULL,
    valid_to date NOT NULL DEFAULT DATE '9999-12-31',
    is_current boolean NOT NULL DEFAULT true,
    source_hash char(64) NOT NULL,
    CHECK (valid_to >= valid_from)
);
CREATE UNIQUE INDEX IF NOT EXISTS uq_dim_customer_current
    ON marts.dim_customer(customer_id) WHERE is_current;
CREATE INDEX IF NOT EXISTS idx_dim_customer_history
    ON marts.dim_customer(customer_id, valid_from, valid_to);

CREATE TABLE IF NOT EXISTS marts.dim_product (
    product_key bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    product_id text NOT NULL UNIQUE,
    product_name text NOT NULL,
    category text NOT NULL,
    brand text NOT NULL,
    active boolean NOT NULL,
    source_hash char(64) NOT NULL
);

CREATE TABLE IF NOT EXISTS marts.dim_store (
    store_key bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    store_id text NOT NULL UNIQUE,
    store_name text NOT NULL,
    city text NOT NULL,
    state char(2) NOT NULL,
    region text NOT NULL,
    opened_at date NOT NULL,
    source_hash char(64) NOT NULL
);

CREATE TABLE IF NOT EXISTS marts.dim_channel (
    channel_key smallint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    channel_name text NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS marts.dim_promotion (
    promotion_key bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    promotion_id text NOT NULL UNIQUE,
    promotion_name text NOT NULL,
    start_date date NOT NULL,
    end_date date NOT NULL,
    discount_rate numeric(5,4) NOT NULL
);

CREATE TABLE IF NOT EXISTS marts.fact_sales (
    sales_key bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    order_item_id text NOT NULL UNIQUE,
    order_id text NOT NULL,
    date_key integer NOT NULL REFERENCES marts.dim_date(date_key),
    customer_key bigint NOT NULL REFERENCES marts.dim_customer(customer_key),
    product_key bigint NOT NULL REFERENCES marts.dim_product(product_key),
    store_key bigint REFERENCES marts.dim_store(store_key),
    channel_key smallint NOT NULL REFERENCES marts.dim_channel(channel_key),
    promotion_key bigint REFERENCES marts.dim_promotion(promotion_key),
    payment_method text NOT NULL,
    order_status text NOT NULL,
    quantity integer NOT NULL,
    unit_price numeric(12,2) NOT NULL,
    unit_cost numeric(12,2) NOT NULL,
    gross_revenue numeric(14,2) NOT NULL,
    discount_amount numeric(14,2) NOT NULL,
    net_revenue numeric(14,2) NOT NULL,
    cost_of_goods numeric(14,2) NOT NULL,
    gross_margin numeric(14,2) NOT NULL,
    loaded_at timestamptz NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS idx_fact_sales_date ON marts.fact_sales(date_key);
CREATE INDEX IF NOT EXISTS idx_fact_sales_customer ON marts.fact_sales(customer_key);
CREATE INDEX IF NOT EXISTS idx_fact_sales_product ON marts.fact_sales(product_key);

CREATE TABLE IF NOT EXISTS marts.fact_inventory_snapshot (
    inventory_key bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    date_key integer NOT NULL REFERENCES marts.dim_date(date_key),
    store_key bigint NOT NULL REFERENCES marts.dim_store(store_key),
    product_key bigint NOT NULL REFERENCES marts.dim_product(product_key),
    on_hand_quantity integer NOT NULL,
    reorder_point integer NOT NULL,
    lead_time_days integer NOT NULL,
    loaded_at timestamptz NOT NULL DEFAULT now(),
    UNIQUE (date_key, store_key, product_key)
);
CREATE INDEX IF NOT EXISTS idx_inventory_product_store
    ON marts.fact_inventory_snapshot(product_key, store_key, date_key);
