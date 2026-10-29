import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]


class PowerBiAssetTests(unittest.TestCase):
    def test_theme_is_valid_json_and_has_accessible_palette(self) -> None:
        theme = json.loads((ROOT / "powerbi/theme.json").read_text(encoding="utf-8"))
        self.assertGreaterEqual(len(theme["dataColors"]), 6)
        self.assertEqual(theme["background"], "#F8FAFC")
        self.assertNotEqual(theme["good"], theme["bad"])

    def test_core_measures_exist_and_use_safe_division(self) -> None:
        dax = (ROOT / "powerbi/measures.dax").read_text(encoding="utf-8")
        for measure in ["Receita Líquida", "Margem %", "Ticket Médio", "Crescimento YoY %", "Taxa de Recompra %"]:
            self.assertIn(measure + " =", dax)
        self.assertGreaterEqual(dax.count("DIVIDE("), 5)

    def test_dashboard_defines_four_business_pages(self) -> None:
        spec = (ROOT / "powerbi/dashboard_spec.md").read_text(encoding="utf-8")
        for page in ["Visão executiva", "Comercial", "Clientes", "Estoque"]:
            self.assertIn(page, spec)


if __name__ == "__main__":
    unittest.main()
