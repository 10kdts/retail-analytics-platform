from pathlib import Path
import unittest

from src.retail_data.quality import build_report, render_markdown


class QualityReportTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.report = build_report(Path("data/sample"))

    def test_quality_contract_detects_all_documented_issues(self) -> None:
        self.assertEqual(self.report["contract"]["status"], "passed")
        self.assertEqual(self.report["summary"]["documented_issues_detected"], 5)
        self.assertEqual(self.report["summary"]["documented_issues"], 5)

    def test_report_counts_are_consistent(self) -> None:
        summary = self.report["summary"]
        self.assertEqual(summary["valid_rows"] + summary["rejected_rows"], summary["rows"])
        self.assertGreater(summary["cascading_rejections"], 0)

    def test_markdown_contains_management_summary(self) -> None:
        markdown = render_markdown(self.report)
        self.assertIn("Taxa de validade", markdown)
        self.assertIn("Contrato de qualidade", markdown)
        self.assertIn("Qualidade por fonte", markdown)
