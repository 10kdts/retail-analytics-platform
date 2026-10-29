from __future__ import annotations

import csv
import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from src.retail_data.generate import generate_dataset


def file_hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class GenerateDatasetTests(unittest.TestCase):
    def temporary_directory(self) -> tempfile.TemporaryDirectory:
        # Manter temporários no repositório também torna a suíte compatível com sandboxes.
        return tempfile.TemporaryDirectory(dir=Path.cwd())

    def test_same_seed_produces_identical_files(self) -> None:
        with self.temporary_directory() as first, self.temporary_directory() as second:
            generate_dataset(Path(first), seed=77, order_count=80)
            generate_dataset(Path(second), seed=77, order_count=80)
            first_hashes = {p.name: file_hash(p) for p in Path(first).iterdir()}
            second_hashes = {p.name: file_hash(p) for p in Path(second).iterdir()}
            self.assertEqual(first_hashes, second_hashes)

    def test_manifest_matches_generated_rows(self) -> None:
        with self.temporary_directory() as directory:
            target = Path(directory)
            manifest = generate_dataset(target, order_count=80)
            stored = json.loads((target / "manifest.json").read_text(encoding="utf-8"))
            self.assertEqual(manifest, stored)
            for filename, expected_count in manifest["row_counts"].items():
                with (target / filename).open(encoding="utf-8-sig", newline="") as stream:
                    self.assertEqual(sum(1 for _ in csv.DictReader(stream)), expected_count)

    def test_controlled_quality_issues_can_be_enabled_or_disabled(self) -> None:
        with self.temporary_directory() as dirty, self.temporary_directory() as clean:
            dirty_manifest = generate_dataset(Path(dirty), order_count=80)
            clean_manifest = generate_dataset(Path(clean), order_count=80, inject_quality_issues=False)
            self.assertEqual(dirty_manifest["row_counts"]["expected_quality_issues.csv"], 5)
            self.assertEqual(clean_manifest["row_counts"]["expected_quality_issues.csv"], 0)

    def test_orders_never_predate_customer_signup(self) -> None:
        with self.temporary_directory() as directory:
            target = Path(directory)
            generate_dataset(target, order_count=80, inject_quality_issues=False)
            with (target / "customers.csv").open(encoding="utf-8-sig", newline="") as stream:
                signup = {row["customer_id"]: row["signup_date"] for row in csv.DictReader(stream)}
            with (target / "orders.csv").open(encoding="utf-8-sig", newline="") as stream:
                orders = list(csv.DictReader(stream))
            self.assertTrue(all(signup[row["customer_id"]] <= row["order_date"] for row in orders))


if __name__ == "__main__":
    unittest.main()
