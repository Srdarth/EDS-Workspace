#!/usr/bin/env python3
"""
EddY — NeverLost Observer CLI
Pipeline de diagnóstico: Observe → Understand → Identify → Decide

Uso:
    python main.py observe --targets /caminho/pasta1 /caminho/pasta2
    python main.py understand
    python main.py identify
    python main.py decide --dest /destino/organizado
    python main.py report
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from eddy_app.core.config import load_config, save_config
from eddy_app.core.db import connect, ensure_schema
from eddy_app.core.observe import observe
from eddy_app.core.understand import understand
from eddy_app.core.identify import identify
from eddy_app.core.decide import generate_plan


def cmd_observe(args, cfg):
    targets = args.targets or cfg["targets"]
    if not targets:
        print("Erro: nenhum target definido. Use --targets ou configure targets.json")
        sys.exit(1)
    db_path = Path(cfg["db_path"])
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = connect(db_path)
    ensure_schema(conn)
    conn.close()
    result = observe(
        db_path=db_path,
        targets=targets,
        exclude_contains=cfg.get("exclude_contains", []),
        logger=print,
        mark_missing=cfg.get("mark_missing", False),
        resume_scan=cfg.get("resume_scan", True),
    )
    print(f"\nResultado: {result}")


def cmd_understand(args, cfg):
    db_path = Path(cfg["db_path"])
    result = understand(
        db_path=db_path,
        hash_max_bytes=cfg.get("hash_max_bytes", 25 * 1024 * 1024),
        logger=print,
        resume_scan=cfg.get("resume_scan", True),
    )
    print(f"\nResultado: {result}")


def cmd_identify(args, cfg):
    db_path = Path(cfg["db_path"])
    result = identify(
        db_path=db_path,
        max_bytes=cfg.get("identify_max_bytes", 50 * 1024 * 1024),
        max_per_run=cfg.get("identify_max_per_run", 50000),
        timebox=cfg.get("identify_timebox", 600),
        text_preview_chars=cfg.get("text_preview_chars", 400),
        name_confidence_min=cfg.get("name_confidence_min", 60),
        logger=print,
        resume_scan=cfg.get("resume_scan", True),
    )
    print(f"\nResultado: {result}")


def cmd_decide(args, cfg):
    db_path = Path(cfg["db_path"])
    dest_root = Path(args.dest or cfg.get("dest_root", "EddY_Organizado"))
    result = generate_plan(
        db_path=db_path,
        dest_root=dest_root,
        rules=cfg.get("rules", []),
        fallback_dest=cfg.get("fallback_dest", "_INBOX"),
        quarantine_dir=cfg.get("quarantine_dir", "_QUARANTINE"),
        plan_duplicates=cfg.get("plan_duplicates", False),
        logger=print,
    )
    print(f"\nResultado: {result}")
    if cfg.get("dry_run", True):
        print("\n[DRY RUN] Nenhum arquivo foi movido. Execute com dry_run=False para efetivar.")


def cmd_report(args, cfg):
    """Gera relatório resumido do banco."""
    import sqlite3
    db_path = Path(cfg["db_path"])
    if not db_path.exists():
        print("Banco não encontrado. Execute 'observe' primeiro.")
        return
    conn = sqlite3.connect(str(db_path))
    cur = conn.cursor()

    total = cur.execute("SELECT COUNT(*) FROM files").fetchone()[0]
    by_status = cur.execute(
        "SELECT COALESCE(status,'NULL'), COUNT(*) FROM files GROUP BY status ORDER BY COUNT(*) DESC"
    ).fetchall()
    by_kind = cur.execute(
        "SELECT COALESCE(kind,'—'), COUNT(*), SUM(size) FROM files GROUP BY kind ORDER BY COUNT(*) DESC"
    ).fetchall()
    dups = cur.execute(
        "SELECT COUNT(*) FROM files WHERE duplicate_of IS NOT NULL"
    ).fetchone()[0]
    conn.close()

    print(f"\n{'='*50}")
    print(f"  NeverLost Observer — Relatório do Banco")
    print(f"{'='*50}")
    print(f"  DB: {db_path}")
    print(f"  Total de arquivos: {total:,}")
    print(f"  Duplicatas: {dups:,}")
    print(f"\n  Status:")
    for status, count in by_status:
        print(f"    {status:<20} {count:>10,}")
    print(f"\n  Por tipo:")
    for kind, count, size in by_kind:
        mb = (size or 0) / (1024 * 1024)
        print(f"    {kind:<20} {count:>10,}   {mb:>10.1f} MB")
    print(f"{'='*50}")


def main():
    parser = argparse.ArgumentParser(
        description="EddY NeverLost Observer — Pipeline de diagnóstico digital"
    )
    sub = parser.add_subparsers(dest="cmd")

    p_obs = sub.add_parser("observe", help="Varrer diretórios e registrar arquivos")
    p_obs.add_argument("--targets", nargs="+", help="Diretórios para varrer")

    sub.add_parser("understand", help="Calcular hashes e detectar duplicatas")
    sub.add_parser("identify", help="Extrair metadados de conteúdo (PDF, DOCX, imagens)")

    p_dec = sub.add_parser("decide", help="Gerar plano de organização (dry-run)")
    p_dec.add_argument("--dest", help="Diretório de destino para organização")

    sub.add_parser("report", help="Exibir relatório do banco")

    args = parser.parse_args()
    if not args.cmd:
        parser.print_help()
        sys.exit(0)

    cfg = load_config()

    if args.cmd == "observe":   cmd_observe(args, cfg)
    elif args.cmd == "understand": cmd_understand(args, cfg)
    elif args.cmd == "identify":   cmd_identify(args, cfg)
    elif args.cmd == "decide":     cmd_decide(args, cfg)
    elif args.cmd == "report":     cmd_report(args, cfg)


if __name__ == "__main__":
    main()
