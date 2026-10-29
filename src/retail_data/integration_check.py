"""Falha se a carga integrada violar contagens, reconciliação ou qualidade."""

from __future__ import annotations

import json
from pathlib import Path

from .ingest import connection_string


ROOT = Path(__file__).resolve().parents[2]


def run_checks() -> dict:
    import psycopg

    checks = {}
    with psycopg.connect(connection_string()) as connection:
        with connection.cursor() as cursor:
            cursor.execute("SELECT count(*) FROM staging.customers")
            checks["staging_customers"] = cursor.fetchone()[0]
            cursor.execute("SELECT count(*) FROM staging.orders")
            checks["staging_orders"] = cursor.fetchone()[0]
            cursor.execute("SELECT count(*) FROM marts.fact_sales")
            checks["fact_sales"] = cursor.fetchone()[0]
            cursor.execute("SELECT count(*) FROM marts.fact_inventory_snapshot")
            checks["fact_inventory_snapshot"] = cursor.fetchone()[0]
            cursor.execute((ROOT / "sql/quality/reconciliation.sql").read_text(encoding="utf-8"))
            differences = cursor.fetchone()
            checks["reconciliation_differences"] = [float(value or 0) for value in differences]
            cursor.execute("SELECT status, rows_read, rows_loaded, rows_rejected FROM raw.ingestion_runs ORDER BY started_at DESC LIMIT 1")
            status, read, loaded, rejected = cursor.fetchone()
            checks["latest_run"] = {"status": status, "read": read, "loaded": loaded, "rejected": rejected}

    failures = []
    if checks["staging_customers"] <= 0 or checks["staging_orders"] <= 0: failures.append("staging vazio")
    if checks["fact_sales"] <= 0 or checks["fact_inventory_snapshot"] <= 0: failures.append("marts vazios")
    if any(abs(value) > 0.01 for value in checks["reconciliation_differences"]): failures.append("reconciliação financeira")
    if checks["latest_run"]["status"] != "succeeded": failures.append("última ingestão não concluída")
    checks["status"] = "passed" if not failures else "failed"
    checks["failures"] = failures
    return checks


def main() -> None:
    checks = run_checks(); print(json.dumps(checks, ensure_ascii=False, indent=2))
    if checks["status"] != "passed": raise SystemExit(1)


if __name__ == "__main__":
    main()
