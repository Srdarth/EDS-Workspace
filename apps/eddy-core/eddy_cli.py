#!/usr/bin/env python3
"""
EddY CLI Simplificado para Notebook
Comandos: observe, identify, understand, decide, execute, pipeline
"""
import sys
import os
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "core"))

from core.db import connect, ensure_schema
from core.observe import observe
from core.identify import identify_files
from core.understand import understand
from core.decide import generate_plan
from core.execute import execute_plans
from core.verify import verify
from core.config import load_config


def main():
    if len(sys.argv) < 2:
        print("Uso: python3 eddy_cli.py <comando> [opcoes]")
        print("Comandos: observe, identify, understand, decide, execute, pipeline")
        print("Para executar de verdade: python3 eddy_cli.py execute --apply")
        sys.exit(1)

    cmd = sys.argv[1].lower()
    cfg = load_config()
    db_path = Path(cfg["db_path"])

    print(f"📁 Banco: {db_path}")
    print(f"🎯 Alvos: {cfg['targets']}")
    print(f"📂 Destino: {cfg['dest_root']}")
    print(f"🔒 Dry-run: {cfg['dry_run']}")
    print("-" * 50)

    if cmd == "observe":
        result = observe(
            db_path=db_path,
            targets=cfg["targets"],
            exclude_contains=cfg["exclude_contains"],
            precount=cfg.get("precount", False),
            mark_missing=cfg.get("mark_missing", False),
            resume_scan=cfg.get("resume_scan", False),
            dir_cache=cfg.get("dir_cache", False),
        )
        print(f"\n✅ Observe concluido: {result}")

    elif cmd == "identify":
        result = identify_files(
            db_path=db_path,
            identify_max_bytes=cfg["identify_max_bytes"],
            text_preview_chars=cfg["text_preview_chars"],
            min_confidence=cfg["name_confidence_min"],
            resume_scan=False,
        )
        print(f"\n✅ Identify concluido: {result}")

    elif cmd == "understand":
        result = understand(
            db_path=db_path,
            hash_max_bytes=cfg["hash_max_bytes"],
            resume_scan=False,
        )
        print(f"\n✅ Understand concluido: {result}")

    elif cmd == "decide":
        result = generate_plan(
            db_path=db_path,
            dest_root=Path(cfg["dest_root"]),
            rules=cfg["rules"],
            fallback_dest=cfg["fallback_dest"],
            quarantine_dir=cfg["quarantine_dir"],
            plan_duplicates=cfg.get("plan_duplicates", False),
        )
        print(f"\n✅ Decide concluido: {result}")

    elif cmd == "execute":
        apply = "--apply" in sys.argv
        dry_run = not apply
        if not apply:
            print("⚠️  MODO DRY-RUN (simulação). Nenhum arquivo será movido.")
            print("    Para executar de verdade, adicione --apply")
        
        result = execute_plans(
            db_path=db_path,
            dry_run=dry_run,
            action_mode=cfg["action_mode"],
        )
        print(f"\n✅ Execute concluido: {result}")

    elif cmd == "pipeline":
        print("🚀 Rodando pipeline completo...")
        print("\n[1/6] OBSERVE...")
        observe(db_path=db_path, targets=cfg["targets"], exclude_contains=cfg["exclude_contains"], 
                precount=False, mark_missing=False, resume_scan=False, dir_cache=False)
        
        print("\n[2/6] IDENTIFY...")
        identify_files(db_path=db_path, identify_max_bytes=cfg["identify_max_bytes"],
                       text_preview_chars=cfg["text_preview_chars"], min_confidence=cfg["name_confidence_min"])
        
        print("\n[3/6] UNDERSTAND...")
        understand(db_path=db_path, hash_max_bytes=cfg["hash_max_bytes"])
        
        print("\n[4/6] DECIDE...")
        generate_plan(
            db_path=db_path,
            dest_root=Path(cfg["dest_root"]),
            rules=cfg["rules"],
            fallback_dest=cfg["fallback_dest"],
            quarantine_dir=cfg["quarantine_dir"],
            plan_duplicates=cfg.get("plan_duplicates", False),
        )
        
        print("\n[5/6] EXECUTE (dry-run)...")
        execute_plans(db_path=db_path, dry_run=True, action_mode=cfg["action_mode"])
        
        print("\n[6/6] VERIFY...")
        verify(db_path=db_path, hash_max_bytes=cfg["hash_max_bytes"])
        
        print("\n✅ Pipeline completo (dry-run).")
        print("    Para executar fisicamente, rode: python3 eddy_cli.py execute --apply")

    else:
        print(f"❌ Comando desconhecido: {cmd}")
        sys.exit(1)


if __name__ == "__main__":
    main()
