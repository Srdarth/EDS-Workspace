#!/usr/bin/env python3
import sqlite3
from pathlib import Path

conn = sqlite3.connect('eddy.db')
cur = conn.cursor()

print("📋 PRIMEIROS 10 PLANOS (o que vai acontecer):")
print("=" * 70)

for row in cur.execute('SELECT src_path, dest_path, action, reason FROM plans WHERE status="proposed" LIMIT 10'):
    src = Path(row[0]).name
    dest = Path(row[1]).name
    dest_dir = Path(row[1]).parent.name
    print(f"{row[2]:8} | {src:35} -> {dest_dir}/{dest}")
    print(f"         motivo: {row[3]}")
    print()

print("📊 RESUMO POR TIPO:")
for row in cur.execute('SELECT reason, COUNT(*) FROM plans WHERE status="proposed" GROUP BY reason'):
    print(f"  {row[0]:20} : {row[1]:4} arquivos")

print()
total = cur.execute('SELECT COUNT(*) FROM plans WHERE status="proposed"').fetchone()[0]
print(f"📦 TOTAL: {total} planos")

conn.close()
