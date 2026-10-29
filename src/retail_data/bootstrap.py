"""Aplica scripts SQL versionados ao PostgreSQL."""

from __future__ import annotations

import argparse
from pathlib import Path

from .ingest import connection_string


ROOT = Path(__file__).resolve().parents[2]
INIT_SCRIPTS = [ROOT / "sql/init/001_schemas.sql", ROOT / "sql/init/002_staging.sql", ROOT / "sql/observability/001_pipeline_health.sql"]
MART_SCRIPTS = [ROOT / "sql/marts/001_dimensions_and_facts.sql", ROOT / "sql/marts/002_load_marts.sql", ROOT / "sql/marts/003_semantic_views.sql"]


def apply_scripts(paths: list[Path]) -> None:
    try:
        import psycopg
    except ImportError as exc:
        raise RuntimeError("Instale as dependências com: pip install -e .") from exc
    with psycopg.connect(connection_string(), autocommit=True) as connection:
        with connection.cursor() as cursor:
            for path in paths:
                cursor.execute(path.read_text(encoding="utf-8"))
                print(f"applied={path.relative_to(ROOT)}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--marts", action="store_true", help="Aplica dimensões, fatos e views")
    args = parser.parse_args()
    apply_scripts(MART_SCRIPTS if args.marts else INIT_SCRIPTS)


if __name__ == "__main__":
    main()
