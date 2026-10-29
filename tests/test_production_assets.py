from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]


class ProductionAssetTests(unittest.TestCase):
    def test_ci_runs_database_integration(self) -> None:
        workflow = (ROOT / ".github/workflows/ci.yml").read_text(encoding="utf-8")
        for command in ["retail_data.bootstrap", "retail_data.ingest", "retail_data.integration_check"]:
            self.assertIn(command, workflow)
        self.assertIn("postgres:16-alpine", workflow)

    def test_workflows_use_minimal_read_permission_by_default(self) -> None:
        workflow = (ROOT / ".github/workflows/ci.yml").read_text(encoding="utf-8")
        self.assertIn("contents: read", workflow)

    def test_runbook_covers_core_incidents(self) -> None:
        runbook = (ROOT / "docs/runbook.md").read_text(encoding="utf-8")
        for topic in ["banco indisponível", "aumento de rejeições", "reconciliação"]:
            self.assertIn(topic, runbook)


if __name__ == "__main__":
    unittest.main()
