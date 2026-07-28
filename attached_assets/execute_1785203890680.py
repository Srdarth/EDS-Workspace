from __future__ import annotations

import shutil
import sqlite3
import time
import hashlib
from pathlib import Path
from datetime import datetime, timezone

from .db import connect, start_run, finish_run, insert_action, update_action
from .config import load_config
from .utils import should_exclude


def _log(logger, msg: str):
    if logger:
        logger(msg)
    else:
        print(msg)


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _human_size(n: int) -> str:
    try:
        n = int(n)
    except Exception:
        return "?"
    for unit in ["B", "KB", "MB", "GB", "TB"]:
        if n < 1024:
            return f"{n:.0f}{unit}"
        n /= 1024
    return f"{n:.1f}PB"


def _location_root(path: str) -> str:
    p = Path(path)
    if p.drive:
        return f"{p.drive}\\"
    if p.anchor:
        return p.anchor
    return ""


def _sha256_full(path: Path) -> str | None:
    try:
        h = hashlib.sha256()
        with open(path, "rb") as f:
            while True:
                b = f.read(1024 * 1024)
                if not b:
                    break
                h.update(b)
        return h.hexdigest()
    except Exception:
        return None


def _sha256_limited(path: Path, max_bytes: int | None) -> str | None:
    try:
        h = hashlib.sha256()
        with open(path, "rb") as f:
            chunk = 1024 * 1024
            while True:
                b = f.read(chunk)
                if not b:
                    break
                h.update(b)
        return h.hexdigest()
    except Exception:
        return None


def _md5_full(path: Path) -> str | None:
    try:
        h = hashlib.md5()
        with open(path, "rb") as f:
            chunk = 1024 * 1024
            while True:
                b = f.read(chunk)
                if not b:
                    break
                h.update(b)
        return h.hexdigest()
    except Exception:
        return None


def _hash_pack(md5: str | None, sha256: str | None) -> str | None:
    parts = []
    if md5:
        parts.append(f"md5={md5}")
    if sha256:
        parts.append(f"sha256={sha256}")
    return ";".join(parts) if parts else None


def _record_location(conn, src: str, dest: str, action: str, logger=None):
    try:
        row = conn.execute("SELECT id FROM files WHERE path=? LIMIT 1", (src,)).fetchone()
        if not row:
            row = conn.execute("SELECT id FROM files WHERE organized_path=? LIMIT 1", (src,)).fetchone()
        file_id = row[0] if row else None
        conn.execute(
            """
            INSERT OR IGNORE INTO file_locations
                (file_id, file_path, location_path, location_root, action, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (file_id, src, dest, _location_root(dest), action, _utc_now()),
        )
    except Exception as exc:
        _log(logger, f"WARN: failed to store file location for {src}: {exc}")


def _record_organized_path(conn, src: str, dest: str, moved: bool, logger=None):
    try:
        dest_name = Path(dest).name
        if moved:
            try:
                conn.execute(
                    "UPDATE files SET path=?, organized_path=?, filename=? WHERE path=?",
                    (dest, dest, dest_name, src),
                )
                _record_location(conn, src, dest, "move", logger)
                return
            except sqlite3.IntegrityError:
                conn.execute(
                    "UPDATE files SET organized_path=? WHERE path=?",
                    (dest, src),
                )
                _record_location(conn, src, dest, "move", logger)
                return
        conn.execute("UPDATE files SET organized_path=? WHERE path=?", (dest, src))
        _record_location(conn, src, dest, "copy", logger)
    except Exception as exc:
        _log(logger, f"WARN: failed to store organized_path for {src}: {exc}")


def _create_run(conn, action_mode: str, dry_run: bool) -> tuple[int, str]:
    snapshot = {"action_mode": action_mode, "dry_run": dry_run}
    return start_run(conn, "execute", config_snapshot=snapshot, details=snapshot)


def _finish_run(conn, run_id: int, success: bool):
    finish_run(conn, run_id, success=success)


def _insert_action(
    conn,
    run_id: int,
    src: str,
    action_type: str,
    dest: str,
    reason: str | None,
    status: str,
    hash_src: str | None = None,
    hash_dst: str | None = None,
    error: str | None = None,
    finished_at: str | None = None,
):
    return insert_action(
        conn,
        run_id=run_id,
        src=src,
        dst=dest,
        action_type=action_type,
        status=status,
        reason=reason,
        hash_src=hash_src,
        hash_dst=hash_dst,
        error=error,
        finished_at=finished_at,
    )


def _update_action(conn, action_id: int, status: str, error_msg: str | None = None, hash_dst: str | None = None):
    update_action(conn, action_id, status=status, error=error_msg, hash_dst=hash_dst)


def execute_plans(
    db_path: Path,
    dry_run: bool,
    action_mode: str,
    logger=None,
    progress_cb=None,
    stop_event=None,
):
    conn = connect(db_path)
    cur = conn.cursor()

    cfg = load_config()
    excludes = list(cfg.get("exclude_contains") or [])
    hash_max_bytes = int(cfg.get("hash_max_bytes", 25 * 1024 * 1024))

    total = cur.execute("SELECT COUNT(*) FROM plans WHERE status='proposed'").fetchone()[0]
    if total == 0:
        _log(logger, "Sem planos propostos.")
        conn.close()
        return {"ok": 0, "skip": 0, "fail": 0, "missing": 0}

    total_bytes = 0
    missing_src = 0
    existing_dest = 0
    read_cur = conn.execute("SELECT src_path, dest_path FROM plans WHERE status='proposed'")
    for (src, dest) in read_cur:
        sp = Path(src)
        dp = Path(dest)
        if not sp.exists():
            missing_src += 1
        else:
            try:
                total_bytes += sp.stat().st_size
            except Exception:
                pass
        if dp.exists():
            existing_dest += 1

    _log(
        logger,
        f"Resumo dry itens={total} missing_src={missing_src} dest_exists={existing_dest} total={_human_size(total_bytes)}",
    )

    run_id, run_key = _create_run(conn, action_mode, dry_run)
    conn.commit()

    # Dry-run: registrar PLAN_MKDIR para pastas que terão arquivos (não tocar no disco)
    if dry_run:
        parent_dirs = set()
        for (d,) in conn.execute("SELECT dest_path FROM plans WHERE status='proposed'"):
            parent_dirs.add(str(Path(d).parent))
        for pd in sorted(parent_dirs):
            _insert_action(conn, run_id, "", "PLAN_MKDIR", pd, "needed_by_plan", "PLANNED")
        conn.commit()

    log_dir = db_path.parent / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    log_path = log_dir / f"execute_{run_key}.log"
    undo_path = log_dir / f"undo_{run_key}.txt"

    def append_log(path: Path, line: str):
        try:
            with open(path, "a", encoding="utf-8") as f:
                f.write(line + "\n")
        except Exception:
            pass

    ok = 0
    skip = 0
    fail = 0
    missing = 0
    stopped = False

    exec_cur = conn.execute(
        "SELECT id, src_path, action, dest_path, reason FROM plans WHERE status='proposed' ORDER BY id ASC"
    )
    for idx, (pid, src, action, dest, reason) in enumerate(exec_cur, start=1):
        if stop_event and stop_event.is_set():
            _log(logger, "Parada solicitada.")
            stopped = True
            break
        if progress_cb and (idx == 1 or idx % 5 == 0 or idx == total):
            progress_cb(idx, total, "execute")

        if should_exclude(src, excludes):
            skip += 1
            conn.execute("UPDATE plans SET status=? WHERE id=?", ("excluded", pid))
            _insert_action(conn, run_id, src, "EXCLUDED", dest, "excluded by rule", "SKIPPED")
            continue

        src_p = Path(src)
        dest_p = Path(dest)
        use_action = (action_mode or action)
        action_type = use_action.upper()
        plan_action_type = f"PLAN_{action_type}"

        if not src_p.exists():
            missing += 1
            conn.execute("UPDATE plans SET status=? WHERE id=?", ("missing_src", pid))
            append_log(log_path, f"[MISSING] id={pid} src={src} dest={dest}")
            _insert_action(conn, run_id, src, action_type, dest, reason, "FAILED")
            continue

        if dest_p.exists():
            skip += 1
            conn.execute("UPDATE plans SET status=? WHERE id=?", ("skipped_exists", pid))
            append_log(log_path, f"[SKIP_EXISTS] id={pid} src={src} dest={dest}")
            _insert_action(conn, run_id, src, action_type, dest, reason, "SKIPPED")
            continue

        # Regra B: verificar canônico por conteúdo (content_index)
        cid = None
        try:
            row = conn.execute(
                "SELECT content_id FROM files WHERE path=? OR organized_path=? LIMIT 1",
                (src, src),
            ).fetchone()
            if row:
                cid = row[0]
        except Exception:
            pass
        md5 = _md5_full(src_p)
        sh = _sha256_full(src_p)
        hash_src_pack = _hash_pack(md5, sh)
        try:
            if md5 or sh:
                conn.execute(
                    "UPDATE files SET hash=COALESCE(hash, ?), sha256=COALESCE(sha256, ?) WHERE path=? OR organized_path=?",
                    (md5, sh, src, src),
                )
        except Exception:
            pass
        if not md5 or not sh:
            skip += 1
            conn.execute("UPDATE plans SET status=? WHERE id=?", ("hash_missing", pid))
            append_log(log_path, f"[SKIP_HASH] id={pid} src={src} dest={dest}")
            _insert_action(
                conn,
                run_id,
                src,
                "SKIP_HASH",
                dest,
                "hash missing",
                "SKIPPED",
                hash_src=hash_src_pack,
            )
            continue
        canon = None
        canon_md5 = None
        if sh:
            r = conn.execute("SELECT canonical_path, md5 FROM content_index WHERE sha256=?", (sh,)).fetchone()
            if r:
                canon, canon_md5 = r
                if canon_md5 and canon_md5 != md5:
                    canon = None
        if canon:
            skip += 1
            conn.execute("UPDATE plans SET status=? WHERE id=?", ("skipped_duplicate", pid))
            append_log(log_path, f"[SKIP_DUP] id={pid} src={src} canon={canon}")
            _insert_action(
                conn,
                run_id,
                src,
                "SKIP_DUP",
                canon,
                "duplicate content (canonical exists)",
                "SKIPPED",
                hash_src=hash_src_pack,
            )
            try:
                conn.execute("UPDATE files SET duplicate_of=? WHERE path=?", (canon, src))
            except Exception:
                pass
            _record_location(conn, src, canon, "skip_dup", logger)
            continue

        if dry_run:
            label = "MOVE" if use_action == "move" else "COPY"
            append_log(log_path, f"[DRY] {label} {src} -> {dest}")
            _insert_action(
                conn,
                run_id,
                src,
                plan_action_type,
                dest,
                reason,
                "PLANNED",
                hash_src=hash_src_pack,
            )
            continue

        action_id = _insert_action(
            conn,
            run_id,
            src,
            action_type,
            dest,
            reason,
            "PENDING",
            hash_src=hash_src_pack,
        )
        hash_dst_pack = None
        try:
            # mkdir just-in-time (Regra A)
            dest_p.parent.mkdir(parents=True, exist_ok=True)
            if use_action == "move":
                shutil.copy2(str(src_p), str(dest_p))
                dst_md5 = _md5_full(dest_p)
                dst_sha = _sha256_full(dest_p)
                hash_dst_pack = _hash_pack(dst_md5, dst_sha)
                if not dst_md5 or not dst_sha:
                    raise RuntimeError("hash_missing_after_copy")
                if dst_md5 != md5 or dst_sha != sh:
                    raise RuntimeError("hash_mismatch_after_copy")
                src_p.unlink()
                conn.execute("UPDATE plans SET status=? WHERE id=?", ("done_move", pid))
                _record_organized_path(conn, src, dest, True, logger)
                append_log(log_path, f"[EXEC] MOVE {src} -> {dest}")
            else:
                shutil.copy2(str(src_p), str(dest_p))
                dst_md5 = _md5_full(dest_p)
                dst_sha = _sha256_full(dest_p)
                hash_dst_pack = _hash_pack(dst_md5, dst_sha)
                if dst_md5 and dst_sha and (dst_md5 != md5 or dst_sha != sh):
                    raise RuntimeError("hash_mismatch_after_copy")
                conn.execute("UPDATE plans SET status=? WHERE id=?", ("done_copy", pid))
                _record_organized_path(conn, src, dest, False, logger)
                append_log(log_path, f"[EXEC] COPY {src} -> {dest}")
            # Registrar canônico se não existir
            try:
                st = dest_p.stat()
                if sh or cid:
                    if sh and not conn.execute("SELECT 1 FROM content_index WHERE sha256=?", (sh,)).fetchone():
                        conn.execute(
                            "INSERT INTO content_index(content_id, sha256, md5, canonical_path, size, mtime_ns) VALUES (?,?,?,?,?,?)",
                            (cid, sh, md5, str(dest_p), st.st_size, int(st.st_mtime_ns)),
                        )
                    elif cid and not conn.execute("SELECT 1 FROM content_index WHERE content_id=?", (cid,)).fetchone():
                        conn.execute(
                            "INSERT INTO content_index(content_id, sha256, md5, canonical_path, size, mtime_ns) VALUES (?,?,?,?,?,?)",
                            (cid, sh, md5, str(dest_p), st.st_size, int(st.st_mtime_ns)),
                        )
            except Exception:
                pass
            ok += 1
            append_log(undo_path, str(dest_p))
            _update_action(conn, action_id, "DONE", None, hash_dst=hash_dst_pack)
        except Exception as e:
            fail += 1
            conn.execute("UPDATE plans SET status=? WHERE id=?", ("failed", pid))
            append_log(log_path, f"[FAIL] id={pid} src={src} dest={dest} err={repr(e)}")
            _update_action(conn, action_id, "FAILED", repr(e), hash_dst=hash_dst_pack)

        if idx % 50 == 0:
            conn.commit()
            time.sleep(0.1)

    _finish_run(conn, run_id, success=(fail == 0 and not stopped))
    conn.commit()
    conn.close()

    _log(logger, f"EXECUTAR fim ok={ok} skip={skip} fail={fail} missing={missing}")
    _log(logger, f"Log: {log_path}")
    if not dry_run:
        _log(logger, f"Undo: {undo_path}")
    return {"ok": ok, "skip": skip, "fail": fail, "missing": missing}
