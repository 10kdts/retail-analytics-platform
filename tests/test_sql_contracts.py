from pathlib import Path
import re
import unittest


ROOT = Path(__file__).resolve().parents[1]


class SqlContractTests(unittest.TestCase):
    def test_fact_tables_declare_expected_grain_constraints(self) -> None:
        ddl = (ROOT / "sql/marts/001_dimensions_and_facts.sql").read_text(encoding="utf-8")
        self.assertRegex(ddl, r"order_item_id text NOT NULL UNIQUE")
        self.assertIn("UNIQUE (date_key, store_key, product_key)", ddl)

    def test_all_dimension_foreign_keys_exist_on_sales_fact(self) -> None:
        ddl = (ROOT / "sql/marts/001_dimensions_and_facts.sql").read_text(encoding="utf-8")
        for dimension in ["dim_date", "dim_customer", "dim_product", "dim_store", "dim_channel", "dim_promotion"]:
            self.assertIn(f"REFERENCES marts.{dimension}", ddl)

    def test_load_script_is_transactional_and_idempotent(self) -> None:
        load = (ROOT / "sql/marts/002_load_marts.sql").read_text(encoding="utf-8")
        self.assertTrue(load.lstrip().startswith("BEGIN;"))
        self.assertTrue(load.rstrip().endswith("COMMIT;"))
        self.assertGreaterEqual(len(re.findall(r"ON CONFLICT", load)), 7)

    def test_reconciliation_covers_financial_measures(self) -> None:
        query = (ROOT / "sql/quality/reconciliation.sql").read_text(encoding="utf-8")
        for measure in ["gross_revenue", "discount_amount", "net_revenue", "cost_of_goods"]:
            self.assertIn(measure, query)


if __name__ == "__main__":
    unittest.main()
