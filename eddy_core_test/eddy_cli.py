#!/usr/bin/env python3
"""
EddY CLI - Dry-run por padrao. Execucao real SO com --apply-explicit.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "core"))

from core.observe import observe
from core.identify import identify_files
from core.understand import understand
from core.decide import generate_plan
from core.execute import execute_plans
from core.verify import verify
from core.config import load_config


def main():
    if len(sys.argv) < 2:
        print("=" * 60)
        print("  EDDY CLI - Modo seguro (dry-run padrao)")
        print("=" * 60)
        print()
        print("USO:")
        print("  python3 eddy_cli.py observe              # Cataloga arquivos")
        print("  python3 eddy_cli.py identify             # Extrai metadados")
        print("  python3 eddy_cli.py understand           # Calcula hashes")
        print("  python3 eddy_cli.py decide               # Gera planos")
        print("  python3 eddy_cli.py execute              # SIMULA execucao (dry-run)")
        print("  python3 eddy_cli.py execute --apply      # EXECUTA DE VERDADE")
        print("  python3 eddy_cli.py execute --apply --limit 50")
        print("  python3 eddy_cli.py pipeline             # Pipeline completo (dry-run)")
        print("  python3 eddy_cli.py verify               # Verifica execucoes")
        print()
        print("⚠️  REGRA: --apply e obrigatorio para acao real.")
        print("   Sem --apply, tudo e simulacao.")
        print("=" * 60)
        sys.exit(0)

    cmd = sys.argv[1].lower()
    cfg = load_config()
    db_path = Path(cfg["db_path"])

    # SEMPRE dry-run por padrao. --apply e a unica forma de mudar.
    apply = "--apply" in sys.argv
    dry_run = not apply  # Se nao tem --apply, e dry-run. Ponto final.

    limit = None
    if "--limit" in sys.argv:
        try:
            idx = sys.argv.index("--limit")
            limit = int(sys.argv[idx + 1])
        except (IndexError, ValueError):
            print("❌ Uso: --limit N")
            sys.exit(1)

    print(f"📁 Banco: {db_path}")
    print(f"🎯 Alvos: {cfg['targets']}")
    print(f"📂 Destino: {cfg['dest_root']}")
    print(f"{'🔥 MODO REAL' if not dry_run else '🔒 MODO SIMULACAO (dry-run)'}")
    if limit:
        print(f"📏 Limite: {limit} planos")
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
        if dry_run:
            print("⚠️  SIMULACAO — nenhum arquivo sera movido.")
            print("    Para executar de verdade: python3 eddy_cli.py execute --apply")

        # Aplicar limite no banco se necessario
        if limit and limit > 0:
            import sqlite3
            conn = sqlite3.connect(str(db_path))
            cur = conn.cursor()
            cur.execute('UPDATE plans SET status="on_hold" WHERE status="proposed"')
            cur.execute(f'UPDATE plans SET status="proposed" WHERE id IN (SELECT id FROM plans WHERE status="on_hold" LIMIT {limit})')
            conn.commit()
            ativos = cur.execute('SELECT COUNT(*) FROM plans WHERE status="proposed"').fetchone()[0]
            print(f"📏 Limitado a {ativos} planos ativos")
            conn.close()

        result = execute_plans(
            db_path=db_path,
            dry_run=dry_run,
            action_mode=cfg["action_mode"],
        )
        print(f"\n✅ Execute concluido: {result}")

    elif cmd == "pipeline":
        print("🚀 Pipeline completo (TUDO em dry-run)...")
        print("\n[1/6] OBSERVE...")
        observe(db_path=db_path, targets=cfg["targets"], exclude_contains=cfg["exclude_contains"],
                precount=False, mark_missing=False, resume_scan=False, dir_cache=False)
        print("\n[2/6] IDENTIFY...")
        identify_files(db_path=db_path, identify_max_bytes=cfg["identify_max_bytes"],
                       text_preview_chars=cfg["text_preview_chars"], min_confidence=cfg["name_confidence_min"])
        print("\n[3/6] UNDERSTAND...")
        understand(db_path=db_path, hash_max_bytes=cfg["hash_max_bytes"])
        print("\n[4/6] DECIDE...")
        generate_plan(db_path=db_path, dest_root=Path(cfg["dest_root"]), rules=cfg["rules"],
                      fallback_dest=cfg["fallback_dest"], quarantine_dir=cfg["quarantine_dir"],
                      plan_duplicates=cfg.get("plan_duplicates", False))
        print("\n[5/6] EXECUTE (dry-run)...")
        execute_plans(db_path=db_path, dry_run=True, action_mode=cfg["action_mode"])
        print("\n[6/6] VERIFY...")
        verify(db_path=db_path, hash_max_bytes=cfg["hash_max_bytes"])
        print("\n✅ Pipeline completo (dry-run).")
        print("    Para executar fisicamente:")
        print("    1. python3 eddy_cli.py execute --apply")
        print("    2. python3 eddy_cli.py verify")

    elif cmd == "verify":
        result = verify(db_path=db_path, hash_max_bytes=cfg["hash_max_bytes"])
        print(f"\n✅ Verify concluido: {result}")

    else:
        print(f"❌ Comando desconhecido: {cmd}")
        sys.exit(1)


if __name__ == "__main__":
    main()
