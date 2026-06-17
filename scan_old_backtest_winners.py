import csv
import json
import re
import zipfile
from pathlib import Path

ROOT = Path("/root/skynet")
SKIP_DIRS = {".venv", "venv", "__pycache__", "cache"}

FILES = []
for p in ROOT.rglob("*"):
    if any(part in SKIP_DIRS for part in p.parts):
        continue
    if p.is_file() and p.suffix.lower() in {".zip", ".csv", ".txt", ".md", ".log", ".json"}:
        name = p.name.lower()
        if any(k in name for k in [
            "result", "grid", "backtest", "summary", "winner",
            "smart", "hybrid", "maxopen", "mfe", "dynamic",
            "confirm", "universe", "sltp", "harvest"
        ]):
            FILES.append(p)

def safe_float(x):
    try:
        if x is None:
            return None
        s = str(x).strip().replace("$", "").replace("%", "").replace(",", "")
        if not s:
            return None
        return float(s)
    except Exception:
        return None

def pick_num(row, names):
    lower = {str(k).lower(): v for k, v in row.items()}
    for n in names:
        if n.lower() in lower:
            v = safe_float(lower[n.lower()])
            if v is not None:
                return v
    for k, v in lower.items():
        for n in names:
            if n.lower() in k:
                x = safe_float(v)
                if x is not None:
                    return x
    return None

def row_score(row):
    net = pick_num(row, [
        "net", "net_pnl", "total_net", "pnl", "profit", "final_net",
        "closed_pnl", "total_pnl", "net_usd"
    ])
    pf = pick_num(row, ["pf", "profit_factor"])
    trades = pick_num(row, ["trades", "n", "count", "closed", "total_trades"])
    wr = pick_num(row, ["winrate", "wr", "win_rate"])

    if net is None:
        return None

    return {
        "net": net,
        "pf": pf,
        "trades": trades,
        "wr": wr,
    }

def short_row(row, max_len=260):
    items = []
    for k, v in row.items():
        if v is None or str(v).strip() == "":
            continue
        kk = str(k).strip()
        vv = str(v).strip()
        if len(vv) > 80:
            vv = vv[:77] + "..."
        items.append(f"{kk}={vv}")
    s = " | ".join(items)
    if len(s) > max_len:
        s = s[:max_len] + "..."
    return s

def parse_csv_text(text, source):
    out = []
    lines = text.splitlines()
    if not lines:
        return out

    sample = "\n".join(lines[:5])
    dialects = []
    for delim in [",", ";", "\t", "|"]:
        try:
            dialect = csv.Sniffer().sniff(sample, delimiters=delim)
            dialects.append(dialect)
        except Exception:
            pass

    if not dialects:
        dialects = [csv.excel]

    for dialect in dialects[:2]:
        try:
            reader = csv.DictReader(lines, dialect=dialect)
            for row in reader:
                sc = row_score(row)
                if sc:
                    out.append({
                        "source": source,
                        "kind": "csv",
                        **sc,
                        "row": short_row(row),
                    })
            if out:
                return out
        except Exception:
            pass

    return out

def parse_text_lines(text, source):
    out = []
    for line in text.splitlines():
        low = line.lower()
        if not any(k in low for k in ["net", "pnl", "profit", "pf", "trades", "winrate"]):
            continue

        # ловим net=-1.23 / pnl:+4.56 / pf=1.2 / trades=30
        vals = {}
        for key in ["net", "pnl", "profit", "pf", "trades", "winrate", "wr"]:
            m = re.search(rf"{key}\s*[:=]\s*([+-]?\d+(?:\.\d+)?)", low)
            if m:
                vals[key] = safe_float(m.group(1))

        net = vals.get("net")
        if net is None:
            net = vals.get("pnl")
        if net is None:
            net = vals.get("profit")

        if net is None:
            continue

        out.append({
            "source": source,
            "kind": "text",
            "net": net,
            "pf": vals.get("pf"),
            "trades": vals.get("trades"),
            "wr": vals.get("winrate") or vals.get("wr"),
            "row": line.strip()[:260],
        })
    return out

def parse_json_text(text, source):
    out = []
    try:
        obj = json.loads(text)
    except Exception:
        return out

    stack = [obj]
    while stack:
        x = stack.pop()
        if isinstance(x, dict):
            sc = row_score(x)
            if sc:
                out.append({
                    "source": source,
                    "kind": "json",
                    **sc,
                    "row": short_row(x),
                })
            for v in x.values():
                if isinstance(v, (dict, list)):
                    stack.append(v)
        elif isinstance(x, list):
            for v in x:
                if isinstance(v, (dict, list)):
                    stack.append(v)

    return out

def parse_bytes(data, source):
    try:
        text = data.decode("utf-8", errors="ignore")
    except Exception:
        return []

    out = []
    if source.lower().endswith(".json"):
        out += parse_json_text(text, source)
    out += parse_csv_text(text, source)
    out += parse_text_lines(text, source)
    return out

all_rows = []

for p in FILES:
    try:
        if p.suffix.lower() == ".zip":
            with zipfile.ZipFile(p) as z:
                for name in z.namelist():
                    low = name.lower()
                    if not low.endswith((".csv", ".txt", ".md", ".json", ".log")):
                        continue
                    if any(k in low for k in [
                        "result", "summary", "winner", "grid", "backtest",
                        "smart", "hybrid", "maxopen", "mfe", "dynamic",
                        "confirm", "universe", "sltp", "harvest"
                    ]):
                        try:
                            data = z.read(name)
                            all_rows += parse_bytes(data, f"{p.name}::{name}")
                        except Exception:
                            pass
        else:
            all_rows += parse_bytes(p.read_bytes(), str(p.relative_to(ROOT)))
    except Exception as e:
        pass

# фильтруем явный мусор
clean = []
for r in all_rows:
    net = r.get("net")
    if net is None:
        continue
    trades = r.get("trades")
    pf = r.get("pf")
    # не выкидываем маленькие, но в топе отсортируем
    clean.append(r)

clean.sort(key=lambda r: (
    r.get("net") if r.get("net") is not None else -999999,
    r.get("pf") if r.get("pf") is not None else -999999,
    r.get("trades") if r.get("trades") is not None else -999999,
), reverse=True)

print("=== OLD BACKTEST / GRID WINNER SCAN ===")
print("files_scanned =", len(FILES))
print("rows_found =", len(clean))
print()

print("=== TOP 80 BY NET ===")
for i, r in enumerate(clean[:80], 1):
    print(
        f"{i:02d}. net={r.get('net')} pf={r.get('pf')} trades={r.get('trades')} wr={r.get('wr')} "
        f"| {r['source']} | {r['kind']}"
    )
    print("    ", r["row"])

print()
print("=== TOP WITH TRADES >= 20 IF DETECTED ===")
filtered = [r for r in clean if r.get("trades") is not None and r["trades"] >= 20]
for i, r in enumerate(filtered[:50], 1):
    print(
        f"{i:02d}. net={r.get('net')} pf={r.get('pf')} trades={r.get('trades')} wr={r.get('wr')} "
        f"| {r['source']} | {r['kind']}"
    )
    print("    ", r["row"])
