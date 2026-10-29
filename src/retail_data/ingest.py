"""Valida e carrega CSVs nas camadas raw e staging do PostgreSQL."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import logging
import os
import uuid
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .reliability import RetryPolicy, retry


LOGGER = logging.getLogger("retail_analytics.ingestion")


LOAD_ORDER = [
    "customers.csv", "products.csv", "stores.csv", "promotions.csv",
    "orders.csv", "order_items.csv", "inventory_snapshots.csv",
]
DOMAINS = {
    "channel": {"Loja física", "E-commerce", "Marketplace"},
    "status": {"Completed", "Cancelled", "Returned"},
    "segment": {"Consumer", "Premium", "Small Business"},
}
KEYS = {
    "customers.csv": ["customer_id"], "products.csv": ["product_id"],
    "stores.csv": ["store_id"], "promotions.csv": ["promotion_id"],
    "orders.csv": ["order_id"], "order_items.csv": ["order_item_id"],
    "inventory_snapshots.csv": ["snapshot_date", "store_id", "product_id"],
}


@dataclass(frozen=True)
class Record:
    source: str
    row_number: int
    payload: dict[str, str]
    row_hash: str
    errors: tuple[str, ...] = ()


def _hash(row: dict[str, str]) -> str:
    canonical = json.dumps(row, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def read_sources(data_dir: Path) -> dict[str, list[dict[str, str]]]:
    sources = {}
    for filename in LOAD_ORDER:
        path = data_dir / filename
        if not path.exists():
            raise FileNotFoundError(f"Fonte obrigatória não encontrada: {path}")
        with path.open(encoding="utf-8-sig", newline="") as stream:
            sources[filename] = list(csv.DictReader(stream))
    return sources


def validate_sources(sources: dict[str, list[dict[str, str]]]) -> list[Record]:
    valid_ids: dict[str, set[str]] = {
        "customer": set(), "product": set(), "store": set(),
        "promotion": set(), "order": set(),
    }
    seen_emails: set[str] = set()
    records: list[Record] = []

    for source in LOAD_ORDER:
        for row_number, row in enumerate(sources[source], start=2):
            errors: list[str] = []
            if any(not row.get(key, "").strip() for key in KEYS[source]):
                errors.append("primary_key_required")
            if source == "customers.csv":
                if not row["state"].strip(): errors.append("state_not_null")
                normalized_email = row["email"].strip().lower()
                if normalized_email in seen_emails: errors.append("email_unique")
                seen_emails.add(normalized_email)
            elif source == "products.csv":
                if float(row["unit_cost"]) <= 0 or float(row["list_price"]) <= 0: errors.append("price_positive")
            elif source == "promotions.csv":
                if not 0 <= float(row["discount_rate"]) <= 1: errors.append("discount_rate_range")
            elif source == "orders.csv":
                if row["customer_id"] not in valid_ids["customer"]: errors.append("customer_fk")
                if row["store_id"] and row["store_id"] not in valid_ids["store"]: errors.append("store_fk")
                if row["channel"] not in DOMAINS["channel"]: errors.append("valid_channel")
                if row["status"] not in DOMAINS["status"]: errors.append("valid_status")
            elif source == "order_items.csv":
                if row["order_id"] not in valid_ids["order"]: errors.append("order_fk")
                if row["product_id"] not in valid_ids["product"]: errors.append("product_fk")
                if int(row["quantity"]) <= 0: errors.append("quantity_positive")
                if row["promotion_id"] and row["promotion_id"] not in valid_ids["promotion"]: errors.append("promotion_fk")
            elif source == "inventory_snapshots.csv":
                if row["store_id"] not in valid_ids["store"]: errors.append("store_fk")
                if row["product_id"] not in valid_ids["product"]: errors.append("product_fk")
                if int(row["on_hand_quantity"]) < 0: errors.append("inventory_non_negative")
            records.append(Record(source, row_number, row, _hash(row), tuple(errors)))
            if not errors:
                id_map = {
                    "customers.csv": ("customer", "customer_id"),
                    "products.csv": ("product", "product_id"),
                    "stores.csv": ("store", "store_id"),
                    "promotions.csv": ("promotion", "promotion_id"),
                    "orders.csv": ("order", "order_id"),
                }
                if source in id_map:
                    entity, key = id_map[source]
                    valid_ids[entity].add(row[key])
    return records


def connection_string() -> str:
    return (
        f"host={os.getenv('POSTGRES_HOST', 'localhost')} "
        f"port={os.getenv('POSTGRES_PORT', '5432')} "
        f"dbname={os.getenv('POSTGRES_DB', 'retail_analytics')} "
        f"user={os.getenv('POSTGRES_USER', 'retail_user')} "
        f"password={os.getenv('POSTGRES_PASSWORD', 'change_me')}"
    )


def _typed_values(record: Record) -> list[Any]:
    row = record.payload
    converters = {
        "customers.csv": lambda: [row[k] for k in ["customer_id", "full_name", "email"]] + [int(row["birth_year"])] + [row[k] for k in ["city", "state", "signup_date", "segment"]] + [row["marketing_consent"] == "true"],
        "products.csv": lambda: [row[k] for k in ["product_id", "product_name", "category", "brand"]] + [float(row["unit_cost"]), float(row["list_price"]), row["active"] == "true"],
        "stores.csv": lambda: [row[k] for k in ["store_id", "store_name", "city", "state", "region", "opened_at"]],
        "promotions.csv": lambda: [row[k] for k in ["promotion_id", "promotion_name", "start_date", "end_date"]] + [float(row["discount_rate"])],
        "orders.csv": lambda: [row[k] or None for k in ["order_id", "customer_id", "store_id", "order_date", "channel", "payment_method", "status"]],
        "order_items.csv": lambda: [row[k] for k in ["order_item_id", "order_id", "product_id"]] + [int(row["quantity"]), float(row["unit_price"]), float(row["unit_cost"]), float(row["discount_amount"]), row["promotion_id"] or None],
        "inventory_snapshots.csv": lambda: [row[k] for k in ["snapshot_date", "store_id", "product_id"]] + [int(row["on_hand_quantity"]), int(row["reorder_point"]), int(row["lead_time_days"])],
    }
    return converters[record.source]() + [record.row_hash]


UPSERTS = {
    "customers.csv": "INSERT INTO staging.customers(customer_id,full_name,email,birth_year,city,state,signup_date,segment,marketing_consent,source_hash) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) ON CONFLICT (customer_id) DO UPDATE SET full_name=EXCLUDED.full_name,email=EXCLUDED.email,birth_year=EXCLUDED.birth_year,city=EXCLUDED.city,state=EXCLUDED.state,signup_date=EXCLUDED.signup_date,segment=EXCLUDED.segment,marketing_consent=EXCLUDED.marketing_consent,source_hash=EXCLUDED.source_hash,updated_at=now()",
    "products.csv": "INSERT INTO staging.products(product_id,product_name,category,brand,unit_cost,list_price,active,source_hash) VALUES (%s,%s,%s,%s,%s,%s,%s,%s) ON CONFLICT (product_id) DO UPDATE SET product_name=EXCLUDED.product_name,category=EXCLUDED.category,brand=EXCLUDED.brand,unit_cost=EXCLUDED.unit_cost,list_price=EXCLUDED.list_price,active=EXCLUDED.active,source_hash=EXCLUDED.source_hash,updated_at=now()",
    "stores.csv": "INSERT INTO staging.stores(store_id,store_name,city,state,region,opened_at,source_hash) VALUES (%s,%s,%s,%s,%s,%s,%s) ON CONFLICT (store_id) DO UPDATE SET store_name=EXCLUDED.store_name,city=EXCLUDED.city,state=EXCLUDED.state,region=EXCLUDED.region,opened_at=EXCLUDED.opened_at,source_hash=EXCLUDED.source_hash,updated_at=now()",
    "promotions.csv": "INSERT INTO staging.promotions(promotion_id,promotion_name,start_date,end_date,discount_rate,source_hash) VALUES (%s,%s,%s,%s,%s,%s) ON CONFLICT (promotion_id) DO UPDATE SET promotion_name=EXCLUDED.promotion_name,start_date=EXCLUDED.start_date,end_date=EXCLUDED.end_date,discount_rate=EXCLUDED.discount_rate,source_hash=EXCLUDED.source_hash,updated_at=now()",
    "orders.csv": "INSERT INTO staging.orders(order_id,customer_id,store_id,order_date,channel,payment_method,status,source_hash) VALUES (%s,%s,%s,%s,%s,%s,%s,%s) ON CONFLICT (order_id) DO UPDATE SET customer_id=EXCLUDED.customer_id,store_id=EXCLUDED.store_id,order_date=EXCLUDED.order_date,channel=EXCLUDED.channel,payment_method=EXCLUDED.payment_method,status=EXCLUDED.status,source_hash=EXCLUDED.source_hash,updated_at=now()",
    "order_items.csv": "INSERT INTO staging.order_items(order_item_id,order_id,product_id,quantity,unit_price,unit_cost,discount_amount,promotion_id,source_hash) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s) ON CONFLICT (order_item_id) DO UPDATE SET order_id=EXCLUDED.order_id,product_id=EXCLUDED.product_id,quantity=EXCLUDED.quantity,unit_price=EXCLUDED.unit_price,unit_cost=EXCLUDED.unit_cost,discount_amount=EXCLUDED.discount_amount,promotion_id=EXCLUDED.promotion_id,source_hash=EXCLUDED.source_hash,updated_at=now()",
    "inventory_snapshots.csv": "INSERT INTO staging.inventory_snapshots(snapshot_date,store_id,product_id,on_hand_quantity,reorder_point,lead_time_days,source_hash) VALUES (%s,%s,%s,%s,%s,%s,%s) ON CONFLICT (snapshot_date,store_id,product_id) DO UPDATE SET on_hand_quantity=EXCLUDED.on_hand_quantity,reorder_point=EXCLUDED.reorder_point,lead_time_days=EXCLUDED.lead_time_days,source_hash=EXCLUDED.source_hash,updated_at=now()",
}


def load_database(records: list[Record], data_dir: Path) -> dict[str, int]:
    try:
        import psycopg
    except ImportError as exc:
        raise RuntimeError("Instale as dependências com: pip install -e .") from exc

    run_id = uuid.uuid4()
    read = len(records); rejected = sum(bool(r.errors) for r in records); loaded = 0
    with psycopg.connect(connection_string()) as connection:
        with connection.cursor() as cursor:
            cursor.execute("INSERT INTO raw.ingestion_runs(run_id,status,source_directory) VALUES (%s,'running',%s)", (run_id, str(data_dir)))
            try:
                for record in records:
                    payload = json.dumps(record.payload, ensure_ascii=False)
                    cursor.execute(
                        "INSERT INTO raw.source_records(run_id,source_name,source_row_number,row_hash,payload) VALUES (%s,%s,%s,%s,%s::jsonb) ON CONFLICT (source_name,row_hash) DO NOTHING RETURNING 1",
                        (run_id, record.source, record.row_number, record.row_hash, payload),
                    )
                    is_new = cursor.fetchone() is not None
                    if record.errors:
                        cursor.execute(
                            "INSERT INTO raw.rejections(run_id,source_name,source_row_number,row_hash,payload,error_codes) VALUES (%s,%s,%s,%s,%s::jsonb,%s) ON CONFLICT DO NOTHING",
                            (run_id, record.source, record.row_number, record.row_hash, payload, list(record.errors)),
                        )
                    elif is_new:
                        cursor.execute(UPSERTS[record.source], _typed_values(record)); loaded += 1
                cursor.execute("UPDATE raw.ingestion_runs SET status='succeeded',finished_at=now(),rows_read=%s,rows_loaded=%s,rows_rejected=%s WHERE run_id=%s", (read, loaded, rejected, run_id))
            except Exception as exc:
                connection.rollback()
                with connection.cursor() as failure_cursor:
                    failure_cursor.execute("INSERT INTO raw.ingestion_runs(run_id,status,source_directory,finished_at,error_message) VALUES (%s,'failed',%s,now(),%s) ON CONFLICT (run_id) DO UPDATE SET status='failed',finished_at=now(),error_message=EXCLUDED.error_message", (run_id, str(data_dir), str(exc)))
                raise
    return {"rows_read": read, "rows_loaded": loaded, "rows_rejected": rejected}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-dir", type=Path, default=Path(os.getenv("DATA_DIR", "data/sample")))
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--max-attempts", type=int, default=3)
    args = parser.parse_args()
    logging.basicConfig(
        level=logging.INFO,
        format='{"time":"%(asctime)s","level":"%(levelname)s","logger":"%(name)s","message":"%(message)s"}',
    )
    records = validate_sources(read_sources(args.data_dir))
    summary = {
        "rows_read": len(records),
        "rows_valid": sum(not r.errors for r in records),
        "rows_rejected": sum(bool(r.errors) for r in records),
        "errors": dict(Counter(code for r in records for code in r.errors)),
    }
    if not args.dry_run:
        policy = RetryPolicy(max_attempts=args.max_attempts)
        summary.update(
            retry(
                lambda: load_database(records, args.data_dir),
                policy,
                on_retry=lambda attempt, exc, delay: LOGGER.warning(
                    "retry attempt=%s delay_seconds=%s error=%s", attempt, delay, exc
                ),
            )
        )
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
