from pathlib import Path
import unittest

from src.retail_data.ingest import read_sources, validate_sources


class IngestionValidationTests(unittest.TestCase):
    def test_sample_contains_documented_issues_and_propagates_invalid_parents(self) -> None:
        records = validate_sources(read_sources(Path("data/sample")))
        rejected = [record for record in records if record.errors]
        codes = {code for record in rejected for code in record.errors}
        self.assertEqual(len(records), 5157)
        self.assertTrue({"state_not_null", "email_unique", "valid_channel", "quantity_positive", "order_fk"} <= codes)
        self.assertIn("customer_fk", codes)

        valid_order_ids = {
            record.payload["order_id"] for record in records
            if record.source == "orders.csv" and not record.errors
        }
        valid_items = [
            record for record in records
            if record.source == "order_items.csv" and not record.errors
        ]
        self.assertTrue(all(item.payload["order_id"] in valid_order_ids for item in valid_items))

    def test_all_required_sources_are_read(self) -> None:
        sources = read_sources(Path("data/sample"))
        self.assertEqual(len(sources), 7)


if __name__ == "__main__":
    unittest.main()
