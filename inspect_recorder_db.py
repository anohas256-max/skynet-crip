import sqlite3
from pathlib import Path

DB = Path("/root/skynet/data/skynet_recorder.sqlite3")

print("DB:", DB, "exists=", DB.exists(), "size=", DB.stat().st_size if DB.exists() else 0)

con = sqlite3.connect(DB)
con.row_factory = sqlite3.Row
cur = con.cursor()

tables = cur.execute("""
SELECT name FROM sqlite_master
WHERE type='table'
ORDER BY name
""").fetchall()

print("\n=== TABLES ===")
for t in tables:
    name = t["name"]
    try:
        n = cur.execute(f'SELECT COUNT(*) AS n FROM "{name}"').fetchone()["n"]
    except Exception as e:
        n = f"ERR {type(e).__name__}: {e}"
    print(name, "rows=", n)

print("\n=== SCHEMA + SAMPLE ===")
for t in tables:
    name = t["name"]
    print("\n---", name, "---")
    cols = cur.execute(f'PRAGMA table_info("{name}")').fetchall()
    print("columns:", [c["name"] for c in cols])

    try:
        rows = cur.execute(f'SELECT * FROM "{name}" LIMIT 3').fetchall()
        for r in rows:
            print(dict(r))
    except Exception as e:
        print("sample_error:", type(e).__name__, e)

con.close()
