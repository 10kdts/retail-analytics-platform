"""Gera fontes sintéticas, determinísticas e relacionais de uma operação de varejo."""

from __future__ import annotations

import argparse
import csv
import json
import math
import random
from collections import defaultdict
from datetime import date, timedelta
from pathlib import Path
from typing import Iterable


STATES = [
    ("SP", "São Paulo"),
    ("RJ", "Rio de Janeiro"),
    ("MG", "Belo Horizonte"),
    ("PR", "Curitiba"),
    ("BA", "Salvador"),
    ("PE", "Recife"),
]
CATEGORIES = {
    "Eletrônicos": ["Fone", "Teclado", "Mouse", "Webcam", "Caixa de som"],
    "Casa": ["Luminária", "Organizador", "Jogo de copos", "Toalha", "Almofada"],
    "Esporte": ["Garrafa", "Tapete", "Corda", "Mochila", "Faixa elástica"],
    "Papelaria": ["Caderno", "Caneta", "Planner", "Estojo", "Marcador"],
}
CHANNELS = ["Loja física", "E-commerce", "Marketplace"]
PAYMENTS = ["Cartão", "Pix", "Boleto"]
FIRST_NAMES = [
    "Ana", "Bruno", "Carla", "Daniel", "Eduarda", "Felipe", "Gabriela", "Henrique",
    "Isabela", "João", "Larissa", "Marcos", "Natália", "Otávio", "Paula", "Rafael",
]
LAST_NAMES = [
    "Almeida", "Barbosa", "Cardoso", "Dias", "Ferreira", "Gomes", "Lima", "Martins",
    "Oliveira", "Pereira", "Rocha", "Santos", "Silva", "Souza", "Teixeira", "Vieira",
]


def _write_csv(path: Path, rows: Iterable[dict], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8-sig") as stream:
        writer = csv.DictWriter(stream, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def _random_date(rng: random.Random, start: date, end: date) -> date:
    return start + timedelta(days=rng.randrange((end - start).days + 1))


def _weighted_sales_date(rng: random.Random, start: date, end: date) -> date:
    """Amostra datas com picos de novembro/dezembro e leve crescimento no segundo ano."""
    while True:
        candidate = _random_date(rng, start, end)
        month_factor = {11: 1.75, 12: 1.55, 1: 0.78, 2: 0.82}.get(candidate.month, 1.0)
        year_factor = 1.15 if candidate.year == end.year else 1.0
        weekend_factor = 1.12 if candidate.weekday() >= 5 else 1.0
        if rng.random() < (month_factor * year_factor * weekend_factor) / 2.2:
            return candidate


def _make_stores() -> list[dict]:
    rows = []
    for index, (state, city) in enumerate(STATES, start=1):
        rows.append(
            {
                "store_id": f"S{index:03d}",
                "store_name": f"Loja {city}",
                "city": city,
                "state": state,
                "region": "Sudeste" if state in {"SP", "RJ", "MG"} else "Sul" if state == "PR" else "Nordeste",
                "opened_at": date(2018 + index % 5, (index * 2) % 12 + 1, 1).isoformat(),
            }
        )
    return rows


def _make_products(rng: random.Random, count: int) -> list[dict]:
    rows = []
    category_items = [(category, item) for category, items in CATEGORIES.items() for item in items]
    for index in range(1, count + 1):
        category, item = category_items[(index - 1) % len(category_items)]
        cost = round(rng.uniform(8, 220), 2)
        margin = rng.uniform(1.35, 2.15)
        rows.append(
            {
                "product_id": f"P{index:04d}",
                "product_name": f"{item} {index:02d}",
                "category": category,
                "brand": f"Marca {(index - 1) % 8 + 1}",
                "unit_cost": f"{cost:.2f}",
                "list_price": f"{cost * margin:.2f}",
                "active": "true",
            }
        )
    return rows


def _make_customers(rng: random.Random, count: int, start: date, end: date) -> list[dict]:
    rows = []
    for index in range(1, count + 1):
        first = rng.choice(FIRST_NAMES)
        last = rng.choice(LAST_NAMES)
        state, city = rng.choice(STATES)
        signup = _random_date(rng, start - timedelta(days=540), end - timedelta(days=10))
        rows.append(
            {
                "customer_id": f"C{index:05d}",
                "full_name": f"{first} {last}",
                "email": f"cliente{index:05d}@example.com",
                "birth_year": rng.randint(1958, 2004),
                "city": city,
                "state": state,
                "signup_date": signup.isoformat(),
                "segment": rng.choices(["Consumer", "Premium", "Small Business"], [0.7, 0.2, 0.1])[0],
                "marketing_consent": rng.choices(["true", "false"], [0.72, 0.28])[0],
            }
        )
    return rows


def _make_promotions() -> list[dict]:
    return [
        {"promotion_id": "PR001", "promotion_name": "Volta às aulas", "start_date": "2024-01-15", "end_date": "2024-02-20", "discount_rate": "0.10"},
        {"promotion_id": "PR002", "promotion_name": "Black Friday", "start_date": "2024-11-20", "end_date": "2024-11-30", "discount_rate": "0.20"},
        {"promotion_id": "PR003", "promotion_name": "Natal", "start_date": "2024-12-01", "end_date": "2024-12-24", "discount_rate": "0.12"},
        {"promotion_id": "PR004", "promotion_name": "Volta às aulas", "start_date": "2025-01-15", "end_date": "2025-02-20", "discount_rate": "0.10"},
        {"promotion_id": "PR005", "promotion_name": "Black Friday", "start_date": "2025-11-20", "end_date": "2025-11-30", "discount_rate": "0.22"},
        {"promotion_id": "PR006", "promotion_name": "Natal", "start_date": "2025-12-01", "end_date": "2025-12-24", "discount_rate": "0.12"},
    ]


def _active_promotion(order_date: date, promotions: list[dict]) -> dict | None:
    for promotion in promotions:
        if date.fromisoformat(promotion["start_date"]) <= order_date <= date.fromisoformat(promotion["end_date"]):
            return promotion
    return None


def _make_orders(
    rng: random.Random,
    customers: list[dict],
    products: list[dict],
    stores: list[dict],
    promotions: list[dict],
    count: int,
    start: date,
    end: date,
) -> tuple[list[dict], list[dict]]:
    orders: list[dict] = []
    items: list[dict] = []
    # A distribuição de Pareto cria clientes recorrentes sem tornar todos iguais.
    customer_weights = [1.0 + 5.0 / math.sqrt(index + 1) for index in range(len(customers))]
    product_weights = [1.0 + 3.0 / math.sqrt(index + 1) for index in range(len(products))]

    for order_index in range(1, count + 1):
        order_date = _weighted_sales_date(rng, start, end)
        eligible = [
            (customer, weight)
            for customer, weight in zip(customers, customer_weights)
            if date.fromisoformat(customer["signup_date"]) <= order_date
        ]
        customer = rng.choices(
            [customer for customer, _ in eligible],
            weights=[weight for _, weight in eligible],
            k=1,
        )[0]
        channel = rng.choices(CHANNELS, [0.48, 0.38, 0.14])[0]
        store_id = rng.choice(stores)["store_id"] if channel == "Loja física" else ""
        status = rng.choices(["Completed", "Cancelled", "Returned"], [0.93, 0.04, 0.03])[0]
        promotion = _active_promotion(order_date, promotions)
        order_id = f"O{order_index:07d}"
        orders.append(
            {
                "order_id": order_id,
                "customer_id": customer["customer_id"],
                "store_id": store_id,
                "order_date": order_date.isoformat(),
                "channel": channel,
                "payment_method": rng.choices(PAYMENTS, [0.58, 0.34, 0.08])[0],
                "status": status,
            }
        )

        selected_products = rng.sample(products, k=rng.randint(1, 4))
        for line_number, product in enumerate(selected_products, start=1):
            quantity = rng.choices([1, 2, 3, 4], [0.68, 0.22, 0.08, 0.02])[0]
            unit_price = float(product["list_price"])
            rate = float(promotion["discount_rate"]) if promotion and rng.random() < 0.68 else 0.0
            items.append(
                {
                    "order_item_id": f"{order_id}-{line_number}",
                    "order_id": order_id,
                    "product_id": product["product_id"],
                    "quantity": quantity,
                    "unit_price": f"{unit_price:.2f}",
                    "unit_cost": product["unit_cost"],
                    "discount_amount": f"{quantity * unit_price * rate:.2f}",
                    "promotion_id": promotion["promotion_id"] if rate else "",
                }
            )
    return orders, items


def _make_inventory(rng: random.Random, products: list[dict], stores: list[dict]) -> list[dict]:
    rows = []
    for snapshot in (date(2025, month, 1) for month in range(1, 13)):
        for store in stores:
            for product in products:
                demand_bias = int(product["product_id"][1:]) % 9
                rows.append(
                    {
                        "snapshot_date": snapshot.isoformat(),
                        "store_id": store["store_id"],
                        "product_id": product["product_id"],
                        "on_hand_quantity": max(0, int(rng.gauss(32 - demand_bias, 14))),
                        "reorder_point": 10 + demand_bias,
                        "lead_time_days": rng.randint(3, 14),
                    }
                )
    return rows


def _inject_quality_issues(customers: list[dict], orders: list[dict], items: list[dict]) -> list[dict]:
    issues = [
        {"issue_id": "DQ001", "file": "customers.csv", "record_key": customers[4]["customer_id"], "rule": "state_not_null", "description": "UF ausente"},
        {"issue_id": "DQ002", "file": "customers.csv", "record_key": customers[9]["customer_id"], "rule": "email_unique", "description": "E-mail duplicado"},
        {"issue_id": "DQ003", "file": "orders.csv", "record_key": orders[14]["order_id"], "rule": "valid_channel", "description": "Canal fora do domínio"},
        {"issue_id": "DQ004", "file": "order_items.csv", "record_key": items[19]["order_item_id"], "rule": "quantity_positive", "description": "Quantidade negativa"},
        {"issue_id": "DQ005", "file": "order_items.csv", "record_key": items[24]["order_item_id"], "rule": "order_fk", "description": "Pedido pai inexistente"},
    ]
    customers[4]["state"] = ""
    customers[9]["email"] = customers[8]["email"]
    orders[14]["channel"] = "Social Commerce"
    items[19]["quantity"] = -1
    items[24]["order_id"] = "O9999999"
    return issues


def generate_dataset(
    output_dir: Path,
    seed: int = 42,
    customer_count: int = 120,
    product_count: int = 40,
    order_count: int = 600,
    inject_quality_issues: bool = True,
) -> dict:
    if min(customer_count, product_count, order_count) < 25:
        raise ValueError("customer_count, product_count e order_count devem ser pelo menos 25")

    rng = random.Random(seed)
    start, end = date(2024, 1, 1), date(2025, 12, 31)
    stores = _make_stores()
    products = _make_products(rng, product_count)
    customers = _make_customers(rng, customer_count, start, end)
    promotions = _make_promotions()
    orders, order_items = _make_orders(rng, customers, products, stores, promotions, order_count, start, end)
    inventory = _make_inventory(rng, products, stores)
    issues = _inject_quality_issues(customers, orders, order_items) if inject_quality_issues else []

    tables = {
        "customers.csv": (customers, list(customers[0])),
        "products.csv": (products, list(products[0])),
        "stores.csv": (stores, list(stores[0])),
        "promotions.csv": (promotions, list(promotions[0])),
        "orders.csv": (orders, list(orders[0])),
        "order_items.csv": (order_items, list(order_items[0])),
        "inventory_snapshots.csv": (inventory, list(inventory[0])),
        "expected_quality_issues.csv": (
            issues,
            ["issue_id", "file", "record_key", "rule", "description"],
        ),
    }
    output_dir.mkdir(parents=True, exist_ok=True)
    for filename, (rows, fieldnames) in tables.items():
        _write_csv(output_dir / filename, rows, fieldnames)

    manifest = {
        "dataset": "retail-analytics-synthetic",
        "seed": seed,
        "period_start": start.isoformat(),
        "period_end": end.isoformat(),
        "quality_issues_injected": inject_quality_issues,
        "row_counts": {filename: len(rows) for filename, (rows, _) in tables.items()},
    }
    (output_dir / "manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    return manifest


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=Path("data/sample"))
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--customers", type=int, default=120)
    parser.add_argument("--products", type=int, default=40)
    parser.add_argument("--orders", type=int, default=600)
    parser.add_argument("--clean", action="store_true", help="Não injeta anomalias intencionais")
    args = parser.parse_args()
    manifest = generate_dataset(
        output_dir=args.output,
        seed=args.seed,
        customer_count=args.customers,
        product_count=args.products,
        order_count=args.orders,
        inject_quality_issues=not args.clean,
    )
    print(json.dumps(manifest, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
