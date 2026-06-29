#!/usr/bin/env python3
from pathlib import Path
from datetime import datetime, timezone
import sqlite3
import re

ROOT = Path("/root/skynet")
OUT = ROOT / "research_dashboard_latest.txt"

files = [
    ROOT / "safe_exports/v18_ml_dataset_export.txt",
    ROOT / "safe_exports/v18_path_feature_lab.txt",
    ROOT / "safe_exports/v18_cost_sensitivity_lab.txt",
    ROOT / "safe_exports/v18_feature_mining_lab.txt",
    ROOT / "safe_exports/v18_maker_short_offset_lab.txt",
    ROOT / "safe_exports/offline_edge_hunter.txt",
    ROOT / "safe_exports/high_freq_opportunity_lab.txt",
    ROOT / "safe_exports/fee_intelligence_lab.txt",
    ROOT / "v18_path_feature_lab_latest.txt",
    ROOT / "v18_cost_sensitivity_lab_latest.txt",
    ROOT / "v18_feature_mining_lab_latest.txt",
    ROOT / "v18_maker_short_offset_lab_latest.txt",
    ROOT / "offline_edge_hunter_latest.txt",
    ROOT / "high_freq_opportunity_lab_latest.txt",
    ROOT / "fee_intelligence_lab_latest.txt",
]

dbs = [
    ROOT / "data/skynet_recorder.sqlite3",
    ROOT / "data/v17_microstructure.sqlite3",
    ROOT / "data/v18_micro_paths.sqlite3",
]

interesting = re.compile(
    r"ROBUST|NO ROBUST|TOP|BEST|WORST|cost|COST|net|NET|avg|AVG|pf|PF|"
    r"maker|taker|SHORT|LONG|TP|SL|MFE|MAE|DECISION|signals|rows|train|test",
    re.I,
)

lines = []
lines.append("=" * 120)
lines.append(f"SKYNET RESEARCH DASHBOARD UTC={datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S_UTC')}")
lines.append("=" * 120)
lines.append("Goal: use existing recorder/lab pipeline, not duplicate recorders.")
lines.append("Real remains OFF.")
lines.append("")

lines.append("=== DB INVENTORY ===")
for db in dbs:
    lines.append(f"\nDB {db} exists={db.exists()} size_mb={round(db.stat().st_size/1024/1024,2) if db.exists() else 0}")
    if not db.exists():
        continue
    con = sqlite3.connect(db)
    con.row_factory = sqlite3.Row
    try:
        for r in con.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"):
            name = r["name"]
            try:
                n = con.execute(f'SELECT COUNT(*) n FROM "{name}"').fetchone()["n"]
                lines.append(f"  {name:<32} rows={n}")
            except Exception as e:
                lines.append(f"  {name:<32} ERR={e}")
    finally:
        con.close()

lines.append("")
lines.append("=" * 120)
lines.append("LAB KEY OUTPUTS")
lines.append("=" * 120)

seen = set()
for f in files:
    if not f.exists() or f in seen:
        continue
    seen.add(f)
    lines.append("")
    lines.append("-" * 120)
    lines.append(str(f))
    lines.append("-" * 120)

    txt = f.read_text(errors="ignore").splitlines()
    picked = [x for x in txt if interesting.search(x)]
    if not picked:
        picked = txt[-80:]
    for x in picked[:220]:
        lines.append(x)

lines.append("")
lines.append("=" * 120)
lines.append("MY DECISION RULE")
lines.append("=" * 120)
lines.append("1) If no robust train/test edge after taker cost: no real taker scalping.")
lines.append("2) If only maker-like cost is positive: build maker/limit simulator with queue/fill assumptions.")
lines.append("3) If v18 recorder has too few rows: keep recorder running and stop touching strategy.")
lines.append("4) If a cluster is symbol-only: no strategy.")
lines.append("5) If a cluster is feature-based and net after 0.17% cost is positive: create one tiny shadow lane.")

OUT.write_text("\n".join(lines))
print(OUT)
print("\n".join(lines[:360]))
