from __future__ import annotations

import hashlib
from datetime import datetime, timezone
from pathlib import Path

from .db import connect, start_run, finish_run, insert_action

SAMPLE_HASH_EVERY = 10


def _log(logger, msg: str):
    if logger:
        logger(msg)
    else:
        print(msg)


def file_hash(path: Path, chunk: int = 1024 * 1024) -> str:
    h = hashlib.md5()
    with open(path, "rb") as f:
        while True:
            b = f.read(chunk)
            if not b:
                break
            h.update(b)
    return h.hexdigest()


def file_sha256(path: Path, chunk: int = 1024 * 1024) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while True:
            b = f.read(chunk)
            if not b:
                break
            h.update(b)
    return h.hexdigest()


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _hash_pack(md5: str | None, sha256: str | None) -> str | None:
    parts = []
    if md5:
        parts.append(f"md5={md5}")
    if sha256:
        parts.append(f"sha256={sha256}")
    return ";".join(parts) if parts else None


def verify(db_path: Path, hash_max_bytes: int, logger=None, progress_cb=None, stop_event=None):
    conn = connect(db_path)
    cur = conn.cursor()
    run_id, _run_key = start_run(conn, "verify", config_snapshot={"hash_max_bytes": hash_max_bytes})
    conn.commit()

    total = cur.execute(
        "SELECT COUNT(*) FROM plans WHERE status IN ('done_copy','done_move')"
    ).fetchone()[0]

    if total == 0:
        _log(logger, "Sem planos executados para verificar.")
        finish_run(conn, run_id, success=True, details={"total": 0})
        conn.commit()
        conn.close()
        return {"ok": 0, "fail": 0, "miss": 0, "hashed": 0}

    ok = 0
    fail = 0
    miss = 0
    hashed = 0

    _log(logger, f"VERIFICAR inicio itens={total}")

    read_cur = conn.execute(
        "SELECT id, src_path, dest_path, status FROM plans WHERE status IN ('done_copy','done_move')"
    )
    stopped = False
    for i, (pid, src, dst, status) in enumerate(read_cur, start=1):
        if stop_event and stop_event.is_set():
            _log(logger, "Parada solicitada.")
            stopped = True
            break
        if progress_cb and (i == 1 or i % 10 == 0 or i == total):
            progress_cb(i, total, "verify")

        src_p = Path(src)
        dst_p = Path(dst)

        if not dst_p.exists():
            miss += 1
            cur.execute("UPDATE plans SET status=? WHERE id=?", ("verify_missing", pid))
            insert_action(
                conn,
                run_id=run_id,
                src=src,
                dst=dst,
                action_type="VERIFY",
                status="FAILED",
                reason="missing_dest",
                finished_at=_utc_now(),
            )
            continue

        try:
            src_size = src_p.stat().st_size if src_p.exists() else None
            dst_size = dst_p.stat().st_size
        except Exception:
            fail += 1
            cur.execute("UPDATE plans SET status=? WHERE id=?", ("verify_fail", pid))
            insert_action(
                conn,
                run_id=run_id,
                src=src,
                dst=dst,
                action_type="VERIFY",
                status="FAILED",
                reason="stat_error",
                finished_at=_utc_now(),
            )
            continue

        if src_size is not None and dst_size != src_size:
            fail += 1
            cur.execute("UPDATE plans SET status=? WHERE id=?", ("verify_size_mismatch", pid))
            insert_action(
                conn,
                run_id=run_id,
                src=src,
                dst=dst,
                action_type="VERIFY",
                status="FAILED",
                reason="size_mismatch",
                finished_at=_utc_now(),
            )
            continue

        if src_p.exists():
            try:
                src_h = file_hash(src_p)
                dst_h = file_hash(dst_p)
                src_s = file_sha256(src_p)
                dst_s = file_sha256(dst_p)
                hash_src = _hash_pack(src_h, src_s)
                hash_dst = _hash_pack(dst_h, dst_s)
                hashed += 1
                if src_h != dst_h or src_s != dst_s:
                    fail += 1
                    cur.execute("UPDATE plans SET status=? WHERE id=?", ("verify_hash_mismatch", pid))
                    insert_action(
                        conn,
                        run_id=run_id,
                        src=src,
                        dst=dst,
                        action_type="VERIFY",
                        status="FAILED",
                        reason="hash_mismatch",
                        hash_src=hash_src,
                        hash_dst=hash_dst,
                        finished_at=_utc_now(),
                    )
                    continue
                insert_action(
                    conn,
                    run_id=run_id,
                    src=src,
                    dst=dst,
                    action_type="VERIFY",
                    status="DONE",
                    reason="verified",
                    hash_src=hash_src,
                    hash_dst=hash_dst,
                    finished_at=_utc_now(),
                )
            except Exception:
                fail += 1
                cur.execute("UPDATE plans SET status=? WHERE id=?", ("verify_fail", pid))
                insert_action(
                    conn,
                    run_id=run_id,
                    src=src,
                    dst=dst,
                    action_type="VERIFY",
                    status="FAILED",
                    reason="hash_error",
                    finished_at=_utc_now(),
                )
                continue

        ok += 1
        cur.execute("UPDATE plans SET status=? WHERE id=?", ("verified", pid))

    finish_run(conn, run_id, success=(fail == 0 and not stopped), details={"ok": ok, "fail": fail, "miss": miss})
    conn.commit()
    conn.close()

    _log(logger, f"VERIFICAR fim ok={ok} fail={fail} miss={miss} hashed={hashed}")
    return {"ok": ok, "fail": fail, "miss": miss, "hashed": hashed}
