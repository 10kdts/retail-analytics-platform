"""Produz um relatório auditável de qualidade para as fontes sintéticas."""

from __future__ import annotations

import argparse
import csv
import json
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .ingest import read_sources, validate_sources


def read_expected_issues(data_dir: Path) -> list[dict[str, str]]:
    path = data_dir / "expected_quality_issues.csv"
    with path.open(encoding="utf-8-sig", newline="") as stream:
        return list(csv.DictReader(stream))


def record_key(source: str, payload: dict[str, str]) -> str:
    key_fields = {
        "customers.csv": ["customer_id"],
        "products.csv": ["product_id"],
        "stores.csv": ["store_id"],
        "promotions.csv": ["promotion_id"],
        "orders.csv": ["order_id"],
        "order_items.csv": ["order_item_id"],
        "inventory_snapshots.csv": ["snapshot_date", "store_id", "product_id"],
    }[source]
    return "|".join(payload[field] for field in key_fields)


def build_report(data_dir: Path) -> dict[str, Any]:
    sources = read_sources(data_dir)
    records = validate_sources(sources)
    expected = read_expected_issues(data_dir)
    expected_signatures = {(r["file"], r["record_key"], r["rule"]) for r in expected}
    detected_signatures = {
        (record.source, record_key(record.source, record.payload), error)
        for record in records for error in record.errors
    }
    root_detected = expected_signatures & detected_signatures
    missing_expected = expected_signatures - detected_signatures
    unexpected_root = {
        signature for signature in detected_signatures
        if signature[2] not in {"customer_fk", "order_fk"} and signature not in expected_signatures
    }

    by_source: dict[str, dict[str, Any]] = {}
    grouped = defaultdict(list)
    for record in records:
        grouped[record.source].append(record)
    for source, source_records in grouped.items():
        total = len(source_records)
        rejected = sum(bool(record.errors) for record in source_records)
        by_source[source] = {
            "rows": total,
            "valid_rows": total - rejected,
            "rejected_rows": rejected,
            "validity_rate": round((total - rejected) / total, 6) if total else 1.0,
        }

    rule_counts = Counter(error for record in records for error in record.errors)
    total = len(records)
    rejected = sum(bool(record.errors) for record in records)
    cascading = sum(
        bool(set(record.errors) & {"customer_fk", "order_fk"}) for record in records
    )
    return {
        "dataset": str(data_dir),
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "summary": {
            "rows": total,
            "valid_rows": total - rejected,
            "rejected_rows": rejected,
            "validity_rate": round((total - rejected) / total, 6),
            "documented_issues": len(expected_signatures),
            "documented_issues_detected": len(root_detected),
            "cascading_rejections": cascading,
        },
        "rule_counts": dict(sorted(rule_counts.items())),
        "sources": by_source,
        "contract": {
            "status": "passed" if not missing_expected and not unexpected_root else "failed",
            "missing_expected": [list(item) for item in sorted(missing_expected)],
            "unexpected_root_issues": [list(item) for item in sorted(unexpected_root)],
        },
    }


def render_markdown(report: dict[str, Any]) -> str:
    summary = report["summary"]
    lines = [
        "# Relatório de qualidade dos dados",
        "",
        f"- Linhas avaliadas: **{summary['rows']:,}**",
        f"- Linhas válidas: **{summary['valid_rows']:,}**",
        f"- Linhas rejeitadas: **{summary['rejected_rows']:,}**",
        f"- Taxa de validade: **{summary['validity_rate']:.2%}**",
        f"- Anomalias documentadas detectadas: **{summary['documented_issues_detected']}/{summary['documented_issues']}**",
        f"- Rejeições em cascata: **{summary['cascading_rejections']:,}**",
        f"- Contrato de qualidade: **{report['contract']['status'].upper()}**",
        "",
        "## Qualidade por fonte",
        "",
        "| Fonte | Linhas | Válidas | Rejeitadas | Taxa de validade |",
        "|---|---:|---:|---:|---:|",
    ]
    for source, metrics in report["sources"].items():
        lines.append(
            f"| {source} | {metrics['rows']:,} | {metrics['valid_rows']:,} | "
            f"{metrics['rejected_rows']:,} | {metrics['validity_rate']:.2%} |"
        )
    lines += ["", "## Ocorrências por regra", "", "| Regra | Ocorrências |", "|---|---:|"]
    for rule, count in report["rule_counts"].items():
        lines.append(f"| {rule} | {count:,} |")
    lines += [
        "",
        "## Interpretação",
        "",
        "As rejeições em cascata são intencionais: registros filhos não podem ser publicados quando o pai foi enviado à quarentena. A taxa de validade mede prontidão para staging, enquanto o contrato verifica se as falhas conhecidas foram detectadas corretamente.",
        "",
    ]
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-dir", type=Path, default=Path("data/sample"))
    parser.add_argument("--json-output", type=Path, default=Path("data/quality_report.json"))
    parser.add_argument("--markdown-output", type=Path, default=Path("docs/generated_quality_report.md"))
    args = parser.parse_args()
    report = build_report(args.data_dir)
    args.json_output.parent.mkdir(parents=True, exist_ok=True)
    args.markdown_output.parent.mkdir(parents=True, exist_ok=True)
    args.json_output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    args.markdown_output.write_text(render_markdown(report), encoding="utf-8")
    print(json.dumps(report["summary"] | {"contract": report["contract"]["status"]}, ensure_ascii=False, indent=2))
    if report["contract"]["status"] != "passed":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
