from __future__ import annotations

from pathlib import Path
from datetime import datetime, timezone
import json

from .db import connect, start_run, finish_run, record_error
from .utils import safe_filename


# Extensoes de sistema/lixo que nao devem ser organizadas
_SYSTEM_EXTS = {
    ".dll", ".exe", ".sys", ".cat", ".pak", ".bin", ".msi",
    ".ocx", ".cpl", ".drv", ".scr", ".mui", ".nls", ".manifest",
    ".pyd", ".wixlib", ".wixobj", ".wixpdb",
}

# Fragmentos de caminho que indicam lixo (recuperacao de disco, cache, etc)
_SKIP_PATH_FRAGMENTS = {
    "found.000",
    "found.001",
    "found.002",
    "recup_dir",
    "$recycle.bin",
    "windowsapps",
}


def _log(logger, msg: str):
    if logger:
        logger(msg)
    else:
        print(msg)


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _should_skip_path(path_lower: str) -> bool:
    return any(frag in path_lower for frag in _SKIP_PATH_FRAGMENTS)


def _load_taxonomy(dest_root: Path) -> set[str]:
    tax_path = dest_root.parent / "taxonomy.json"
    try:
        if tax_path.exists():
            data = json.loads(tax_path.read_text(encoding="utf-8"))
            return {
                str(Path(p)).strip("/")
                for p in (data.get("paths") or [])
                if isinstance(p, str)
            }
    except Exception:
        pass
    return set()


def _within_whitelist(dest_root: Path, whitelist: set[str], candidate: Path) -> bool:
    if not whitelist:
        return True
    try:
        rel = candidate.relative_to(dest_root)
    except Exception:
        return False
    cand = str(rel).replace("\\\\", "\\").strip("\\/")
    return any(cand.lower().startswith(w.lower().strip("\\/")) for w in whitelist)


def _resolve_dest(
    path: Path,
    ext: str,
    kind: str,
    rules: list[dict],
    dest_root: Path,
    fallback_dest: str,
    whitelist: set[str],
) -> Path:
    name = path.name.lower()
    ext = (ext or "").lower()

    for rule in rules or []:
        rtype = rule.get("type")

        if rtype == "name_contains":
            keywords = [k.lower() for k in rule.get("keywords", [])]
            if any(k in name for k in keywords if k):
                cand = dest_root / rule.get("dest", fallback_dest)
                return (
                    cand
                    if _within_whitelist(dest_root, whitelist, cand)
                    else dest_root / fallback_dest
                )

        if rtype == "ext_in":
            exts = [e.lower() for e in rule.get("exts", [])]
            if ext in exts:
                cand = dest_root / rule.get("dest", fallback_dest)
                return (
                    cand
                    if _within_whitelist(dest_root, whitelist, cand)
                    else dest_root / fallback_dest
                )

        if rtype == "kind_is" and kind == rule.get("kind"):
            cand = dest_root / rule.get("dest", fallback_dest)
            return (
                cand
                if _within_whitelist(dest_root, whitelist, cand)
                else dest_root / fallback_dest
            )

    if kind:
        cand = dest_root / kind
        return (
            cand
            if _within_whitelist(dest_root, whitelist, cand)
            else dest_root / fallback_dest
        )

    return dest_root / fallback_dest


def generate_plan(
    db_path: Path,
    dest_root: Path,
    rules: list[dict],
    fallback_dest: str,
    quarantine_dir: str,
    plan_duplicates: bool,
    logger=None,
    progress_cb=None,
    stop_event=None,
):
    conn = connect(db_path)
    cur = conn.cursor()

    run_id_db, _run_key = start_run(
        conn,
        "decide",
        config_snapshot={
            "dest_root": str(dest_root),
            "fallback_dest": fallback_dest,
            "quarantine_dir": quarantine_dir,
            "plan_duplicates": plan_duplicates,
        },
    )
    conn.commit()

    where = (
        "WHERE status IN ('new','NEW','moved','MOVED','discovered',"
        "'understood','identified','unchanged') AND path IS NOT NULL"
    )
    total = cur.execute(f"SELECT COUNT(*) FROM files {where}").fetchone()[0]

    _log(logger, f"DECIDIR inicio itens={total}")

    inserted = 0
    skipped_system = 0
    now = _utc_now()
    whitelist = _load_taxonomy(Path(dest_root))

    read_cur = conn.execute(
        f"""SELECT id, path, ext, extension, detected_ext, canonical_name,
            kind, duplicate_of, status
            FROM files {where}"""
    )

    stopped = False

    for i, (
        fid, path_str, ext, extension, detected_ext,
        canonical_name, kind, duplicate_of, status,
    ) in enumerate(read_cur, start=1):

        if stop_event and stop_event.is_set():
            _log(logger, "Parada solicitada.")
            stopped = True
            break

        if progress_cb and (i == 1 or i % 500 == 0 or i == total):
            progress_cb(i, total, "decide")

        if duplicate_of and not plan_duplicates:
            continue

        path_lower = path_str.lower()

        # Ignorar lixo de recuperacao de disco e pastas de sistema
        if _should_skip_path(path_lower):
            skipped_system += 1
            continue

        src_path = Path(path_str)

        # Protege contra PermissionError em arquivos de sistema protegidos
        try:
            exists = src_path.exists()
        except (PermissionError, OSError):
            continue

        if not exists:
            continue

        ext_use = (ext or extension or detected_ext or src_path.suffix).lower()

        # Ignorar executaveis e arquivos de sistema
        if ext_use in _SYSTEM_EXTS:
            skipped_system += 1
            continue

        kind_use = kind

        if duplicate_of and quarantine_dir:
            dest_dir = Path(dest_root) / quarantine_dir
        else:
            dest_dir = _resolve_dest(
                src_path,
                ext_use,
                kind_use,
                rules,
                Path(dest_root),
                fallback_dest,
                whitelist,
            )

        name_src = canonical_name or src_path.name
        dest_name = safe_filename(name_src)
        dest_path = dest_dir / dest_name

        # Evitar plano duplicado para mesmo src
        cur.execute(
            "SELECT 1 FROM plans WHERE src_path=? LIMIT 1", (str(src_path),)
        )
        if cur.fetchone():
            continue

        # Evitar colisao no destino
        cur.execute(
            "SELECT 1 FROM plans WHERE dest_path=? LIMIT 1", (str(dest_path),)
        )
        if cur.fetchone():
            dest_path = dest_dir / f"{dest_path.stem}__dup{fid}{dest_path.suffix}"

        action = "copy"
        reason = "rule_match" if rules else "by_kind"

        if duplicate_of and quarantine_dir:
            action = "quarantine"
            reason = "duplicate"

        cur.execute(
            """
            INSERT INTO plans (src_path, action, dest_path, reason, status, created_at)
            VALUES (?, ?, ?, ?, 'proposed', ?)
            """,
            (str(src_path), action, str(dest_path), reason, now),
        )

        inserted += 1
        cur.execute("UPDATE files SET status='planned' WHERE id=?", (fid,))

        if inserted % 1000 == 0:
            conn.commit()

    try:
        conn.commit()
        finish_run(
            conn,
            run_id_db,
            success=not stopped,
            details={
                "planned": inserted,
                "total": total,
                "skipped_system": skipped_system,
            },
        )
        conn.commit()
        conn.close()

    except Exception as exc:
        try:
            record_error(
                conn,
                run_id=run_id_db,
                stage="decide",
                file_path="",
                error_type=type(exc).__name__,
                error_msg=str(exc),
            )
        except Exception:
            pass
        try:
            finish_run(
                conn,
                run_id_db,
                success=False,
                details={"planned": inserted, "error": type(exc).__name__},
            )
            conn.commit()
        finally:
            conn.close()
        raise

    _log(logger, f"DECIDIR fim planos={inserted} (sistema ignorado={skipped_system})")
    return {"planned": inserted, "skipped_system": skipped_system}
