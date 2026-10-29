"""Renderiza uma prévia SVG da página executiva usando apenas a biblioteca padrão."""

from __future__ import annotations

import argparse
from collections import defaultdict
from datetime import date
from html import escape
from pathlib import Path

from .ingest import read_sources, validate_sources

BLUE, ORANGE, TEAL = "#2563EB", "#F97316", "#0F766E"
INK, MUTED, GRID, BG = "#0F172A", "#64748B", "#E2E8F0", "#F8FAFC"


def money(value: float) -> str:
    return f"R$ {value / 1000:.1f} mil" if abs(value) >= 1000 else f"R$ {value:.0f}"


def build_metrics(data_dir: Path) -> dict:
    sources = read_sources(data_dir)
    records = validate_sources(sources)
    orders = {r.payload["order_id"]: r.payload for r in records if r.source == "orders.csv" and not r.errors and r.payload["status"] == "Completed"}
    products = {row["product_id"]: row for row in sources["products.csv"]}
    monthly = defaultdict(float); category = defaultdict(float); channel = defaultdict(float); margin = 0.0
    for record in records:
        if record.source != "order_items.csv" or record.errors or record.payload["order_id"] not in orders:
            continue
        row = record.payload; order = orders[row["order_id"]]
        revenue = int(row["quantity"]) * float(row["unit_price"]) - float(row["discount_amount"])
        cost = int(row["quantity"]) * float(row["unit_cost"])
        monthly[date.fromisoformat(order["order_date"]).replace(day=1)] += revenue
        category[products[row["product_id"]]["category"]] += revenue - cost
        channel[order["channel"]] += revenue; margin += revenue - cost
    revenue = sum(monthly.values())
    return {"revenue": revenue, "margin": margin, "orders": len(orders), "ticket": revenue / len(orders),
            "monthly": sorted(monthly.items()), "category": category, "channel": channel}


def txt(x: float, y: float, value: str, size: int = 16, color: str = INK, weight: int = 400) -> str:
    return f'<text x="{x}" y="{y}" font-family="Segoe UI,Arial" font-size="{size}" fill="{color}" font-weight="{weight}">{escape(value)}</text>'


def render(data_dir: Path, output: Path) -> None:
    m = build_metrics(data_dir)
    svg = ['<svg xmlns="http://www.w3.org/2000/svg" width="1600" height="900">', f'<rect width="1600" height="900" fill="{BG}"/>',
           txt(48, 52, "Visão executiva", 30, INK, 700), txt(48, 80, "Crescimento com rentabilidade • dados sintéticos 2024–2025", 14, MUTED)]
    cards = [("Receita líquida", money(m["revenue"])), ("Margem bruta", money(m["margin"])), ("Margem %", f"{m['margin']/m['revenue']:.1%}"), ("Pedidos", f"{m['orders']:,}"), ("Ticket médio", money(m["ticket"]))]
    for i, (label, value) in enumerate(cards):
        x = 48 + i * 300; svg += [f'<rect x="{x}" y="108" width="254" height="100" rx="10" fill="white" stroke="{GRID}"/>', txt(x+18, 142, label, 14, MUTED), txt(x+18, 184, value, 27, INK, 700)]

    svg += [f'<rect x="48" y="240" width="960" height="380" rx="10" fill="white" stroke="{GRID}"/>', txt(72, 278, "Receita acelera no fim do ano", 20, INK, 700)]
    values = [v for _, v in m["monthly"]]; maximum = max(values); points = []
    for i, value in enumerate(values): points.append(f"{82+i*(880/max(1,len(values)-1)):.1f},{575-(value/maximum)*245:.1f}")
    for row in range(4):
        y = 330 + row * 75; svg.append(f'<line x1="72" y1="{y}" x2="980" y2="{y}" stroke="{GRID}"/>')
    svg += [f'<polyline points="{" ".join(points)}" fill="none" stroke="{BLUE}" stroke-width="4"/>', txt(72,603,"jan/24",12,MUTED), txt(928,603,"dez/25",12,MUTED)]

    svg += [f'<rect x="1040" y="240" width="512" height="380" rx="10" fill="white" stroke="{GRID}"/>', txt(1064,278,"Margem por categoria",20,INK,700)]
    ranked = sorted(m["category"].items(), key=lambda x:x[1], reverse=True); maximum = max(v for _,v in ranked)
    for i,(label,value) in enumerate(ranked):
        y=320+i*65; width=300*value/maximum; svg += [txt(1064,y+18,label,14,MUTED), f'<rect x="1180" y="{y}" width="{width:.1f}" height="24" rx="4" fill="{TEAL}"/>', txt(1190+width,y+18,money(value),12,MUTED)]

    svg += [f'<rect x="48" y="652" width="600" height="196" rx="10" fill="white" stroke="{GRID}"/>', txt(72,690,"Receita por canal",19,INK,700)]
    channels=sorted(m["channel"].items(),key=lambda x:x[1],reverse=True); maximum=max(v for _,v in channels)
    for i,(label,value) in enumerate(channels):
        x=95+i*175; height=95*value/maximum; svg += [f'<rect x="{x}" y="{805-height:.1f}" width="90" height="{height:.1f}" rx="4" fill="{[BLUE,ORANGE,"#8B5CF6"][i]}"/>',txt(x,828,label,12,MUTED)]
    best_cat=max(m["category"],key=m["category"].get); best_channel=max(m["channel"],key=m["channel"].get)
    svg += [f'<rect x="680" y="652" width="872" height="196" rx="10" fill="#EFF6FF" stroke="#BFDBFE"/>', txt(712,696,"INSIGHT PRINCIPAL",13,BLUE,700), txt(712,744,f"{best_cat} lidera a margem; {best_channel} concentra a maior receita.",20,INK,700), txt(712,786,"Investigue produtos de alta receita e margem abaixo da média antes de ampliar descontos.",14,MUTED), '</svg>']
    output.parent.mkdir(parents=True, exist_ok=True); output.write_text("".join(svg), encoding="utf-8")


def main() -> None:
    parser=argparse.ArgumentParser(description=__doc__); parser.add_argument("--data-dir",type=Path,default=Path("data/sample")); parser.add_argument("--output",type=Path,default=Path("docs/dashboard_preview.svg")); args=parser.parse_args(); render(args.data_dir,args.output); print(args.output)


if __name__ == "__main__": main()
