CREATE TABLE IF NOT EXISTS staging.customers (
    customer_id text PRIMARY KEY,
    full_name text NOT NULL,
    email text NOT NULL UNIQUE,
    birth_year smallint NOT NULL CHECK (birth_year BETWEEN 1900 AND 2100),
    city text NOT NULL,
    state char(2) NOT NULL,
    signup_date date NOT NULL,
    segment text NOT NULL,
    marketing_consent boolean NOT NULL,
    source_hash char(64) NOT NULL,
    updated_at timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS staging.products (
    product_id text PRIMARY KEY, product_name text NOT NULL, category text NOT NULL,
    brand text NOT NULL, unit_cost numeric(12,2) NOT NULL CHECK (unit_cost > 0),
    list_price numeric(12,2) NOT NULL CHECK (list_price > 0), active boolean NOT NULL,
    source_hash char(64) NOT NULL, updated_at timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS staging.stores (
    store_id text PRIMARY KEY, store_name text NOT NULL, city text NOT NULL,
    state char(2) NOT NULL, region text NOT NULL, opened_at date NOT NULL,
    source_hash char(64) NOT NULL, updated_at timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS staging.promotions (
    promotion_id text PRIMARY KEY, promotion_name text NOT NULL, start_date date NOT NULL,
    end_date date NOT NULL CHECK (end_date >= start_date),
    discount_rate numeric(5,4) NOT NULL CHECK (discount_rate BETWEEN 0 AND 1),
    source_hash char(64) NOT NULL, updated_at timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS staging.orders (
    order_id text PRIMARY KEY, customer_id text NOT NULL REFERENCES staging.customers(customer_id),
    store_id text REFERENCES staging.stores(store_id), order_date date NOT NULL,
    channel text NOT NULL CHECK (channel IN ('Loja física', 'E-commerce', 'Marketplace')),
    payment_method text NOT NULL, status text NOT NULL,
    source_hash char(64) NOT NULL, updated_at timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS staging.order_items (
    order_item_id text PRIMARY KEY, order_id text NOT NULL REFERENCES staging.orders(order_id),
    product_id text NOT NULL REFERENCES staging.products(product_id), quantity integer NOT NULL CHECK (quantity > 0),
    unit_price numeric(12,2) NOT NULL, unit_cost numeric(12,2) NOT NULL,
    discount_amount numeric(12,2) NOT NULL CHECK (discount_amount >= 0),
    promotion_id text REFERENCES staging.promotions(promotion_id),
    source_hash char(64) NOT NULL, updated_at timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS staging.inventory_snapshots (
    snapshot_date date NOT NULL, store_id text NOT NULL REFERENCES staging.stores(store_id),
    product_id text NOT NULL REFERENCES staging.products(product_id),
    on_hand_quantity integer NOT NULL CHECK (on_hand_quantity >= 0),
    reorder_point integer NOT NULL CHECK (reorder_point >= 0),
    lead_time_days integer NOT NULL CHECK (lead_time_days > 0),
    source_hash char(64) NOT NULL, updated_at timestamptz NOT NULL DEFAULT now(),
    PRIMARY KEY (snapshot_date, store_id, product_id)
);
