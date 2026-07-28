from __future__ import annotations

import hashlib
from datetime import datetime
from pathlib import Path

from .db import connect, start_run, finish_run, record_error
from .config import load_config
from .utils import should_exclude, mark_excluded

CODE_EXT = {".py", ".js", ".ts", ".html", ".css", ".json", ".yml", ".yaml", ".bat", ".ps1", ".sh"}
DOC_EXT = {".pdf", ".doc", ".docx", ".ppt", ".pptx", ".xls", ".xlsx", ".txt", ".md"}
IMG_EXT = {".jpg", ".jpeg", ".png", ".webp", ".bmp", ".gif", ".heic", ".tiff"}
VID_EXT = {".mp4", ".mov", ".mkv", ".avi", ".wmv", ".webm", ".m4v"}
ARC_EXT = {".zip", ".rar", ".7z", ".tar", ".gz"}


def _log(logger, msg: str):
    if logger:
        logger(msg)
    else:
        print(msg)


def infer_kind(ext: str) -> str:
    ext = (ext or "").lower()
    if ext in IMG_EXT:
        return "imagem"
    if ext in VID_EXT:
        return "video"
    if ext in DOC_EXT:
        return "documento"
    if ext in CODE_EXT:
        return "codigo"
    if ext in ARC_EXT:
        return "arquivo"
    return "outros"


def file_hash(path: Path, chunk: int = 1024 * 1024) -> str | None:
    h = hashlib.md5()
    try:
        with open(path, "rb") as f:
            while True:
                b = f.read(chunk)
                if not b:
                    break
                h.update(b)
        return h.hexdigest()
    except Exception:
        return None


def file_sha256(path: Path, chunk: int = 1024 * 1024) -> str | None:
    h = hashlib.sha256()
    try:
        with open(path, "rb") as f:
            while True:
                b = f.read(chunk)
                if not b:
                    break
                h.update(b)
        return h.hexdigest()
    except Exception:
        return None


def understand(db_path: Path, hash_max_bytes: int, logger=None, progress_cb=None, stop_event=None, resume_scan: bool = False):
    conn = connect(db_path)
    cur = conn.cursor()
    run_id_db, _run_key = start_run(
        conn,
        "understand",
        config_snapshot={"hash_max_bytes": hash_max_bytes},
    )
    conn.commit()

    # Regra D: excludes globais e retroativos (idempotente)
    try:
        cfg = load_config()
        excludes = list(cfg.get("exclude_contains") or [])
        mark_excluded(conn, excludes)
    except Exception:
        excludes = []

    where = """
        WHERE COALESCE(status,'') NOT IN ('missing','excluded','skip_perm','corrupt','understood')
          AND (
            status IN ('new','NEW','moved','MOVED','discovered','unchanged','identified')
            OR status IS NULL
            OR kind IS NULL OR kind=''
            OR hash IS NULL OR hash=''
          )
    """
    run_id = str(run_id_db)
    last_id = 0
    if resume_scan:
        row = cur.execute(
            "SELECT last_path, status FROM scan_state WHERE target=?", ("__understand__",)
        ).fetchone()
        if row and row[1] == "running" and row[0]:
            try:
                last_id = int(row[0])
                _log(logger, f"Retomar entender do id>{last_id}")
            except Exception:
                last_id = 0

    def update_state(last: int | None, status: str):
        cur.execute(
            """
            INSERT INTO scan_state (target, last_path, run_id, updated_at, status)
            VALUES (?, ?, ?, datetime('now'), ?)
            ON CONFLICT(target) DO UPDATE SET
              last_path=excluded.last_path,
              run_id=excluded.run_id,
              updated_at=excluded.updated_at,
              status=excluded.status
            """,
            ("__understand__", str(last) if last is not None else None, run_id, status),
        )

    update_state(last_id or None, "running")
    conn.commit()

    total = cur.execute(
        f"SELECT COUNT(*) FROM files {where}" + (" AND id > ?" if last_id else ""),
        (last_id,) if last_id else (),
    ).fetchone()[0]

    _log(logger, f"ENTENDER inicio itens={total}")
    updated = 0
    error_count = 0

    def _record_error(path_str: str, err_type: str, exc: Exception):
        nonlocal error_count
        error_count += 1
        try:
            record_error(
                conn,
                run_id=run_id_db,
                stage="understand",
                file_path=path_str,
                error_type=err_type,
                error_msg=str(exc),
            )
        except Exception:
            pass

    query = (
        "SELECT id, path, ext, extension, detected_ext, kind, hash, sha256, size, status, duplicate_of, content_id "
        f"FROM files {where}"
    )
    params = []
    if last_id:
        query += " AND id > ?"
        params.append(last_id)
    read_cur = conn.execute(query, params)
    stopped = False
    for i, (fid, path_str, ext, extension, detected_ext, kind, hval, sha_val, size, status, duplicate_of, content_id) in enumerate(
        read_cur, start=1
    ):
        if status == "excluded":
            continue
        if should_exclude(path_str, excludes):
            try:
                cur.execute("UPDATE files SET status='excluded' WHERE id=?", (fid,))
            except Exception:
                pass
            continue
        if stop_event and stop_event.is_set():
            _log(logger, "Parada solicitada.")
            update_state(fid, "running")
            conn.commit()
            stopped = True
            break
        if progress_cb and (i == 1 or i % 500 == 0 or i == total):
            progress_cb(i, total, "understand")

        if duplicate_of:
            row = conn.execute(
                "SELECT kind, category, hash, sha256 FROM files WHERE path=?",
                (duplicate_of,),
            ).fetchone()
            if row and any(row):
                dup_kind, dup_category, dup_hash, dup_sha = row
                cur.execute(
                    """
                    UPDATE files
                    SET kind=?, category=?, hash=?, sha256=?, status=?
                    WHERE id=?
                    """,
                    (
                        dup_kind,
                        dup_category,
                        dup_hash,
                        dup_sha,
                        "understood",
                        fid,
                    ),
                )
                updated += 1
                if updated % 1000 == 0:
                    update_state(fid, "running")
                    conn.commit()
                continue

        if content_id:
            row = conn.execute(
                "SELECT kind, category, hash, sha256 FROM files WHERE content_id=? AND (kind IS NOT NULL OR hash IS NOT NULL OR sha256 IS NOT NULL) LIMIT 1",
                (content_id,),
            ).fetchone()
            if row and any(row):
                dup_kind, dup_category, dup_hash, dup_sha = row
                cur.execute(
                    """
                    UPDATE files
                    SET kind=?, category=?, hash=?, sha256=?, status=?
                    WHERE id=?
                    """,
                    (
                        dup_kind,
                        dup_category,
                        dup_hash,
                        dup_sha,
                        "understood",
                        fid,
                    ),
                )
                updated += 1
                if updated % 1000 == 0:
                    update_state(fid, "running")
                    conn.commit()
                continue

        try:
            path = Path(path_str)
            if not ext:
                ext = detected_ext or extension or path.suffix.lower()
            if not kind:
                kind = infer_kind(ext)

            category = kind

            new_hash = hval
            new_sha = sha_val
            if path.exists() and path.is_file():
                if not hval:
                    new_hash = file_hash(path)
                if not sha_val:
                    new_sha = file_sha256(path)

            new_status = status or "discovered"
            if status in (None, "new", "moved", "unchanged", "discovered", "identified"):
                new_status = "understood"

            cur.execute(
                """
                UPDATE files
                SET ext=?, extension=?, kind=?, category=?, hash=?, sha256=?, status=?
                WHERE id=?
                """,
                (ext, ext, kind, category, new_hash, new_sha, new_status, fid),
            )
            updated += 1
            if updated % 1000 == 0:
                update_state(fid, "running")
                conn.commit()
        except PermissionError as exc:
            try:
                cur.execute("UPDATE files SET status='skip_perm' WHERE id=?", (fid,))
            except Exception:
                pass
            _record_error(path_str, "PermissionError", exc)
            continue
        except (OSError, ValueError, AttributeError, TypeError, Exception) as exc:
            try:
                cur.execute("UPDATE files SET status='corrupt' WHERE id=?", (fid,))
            except Exception:
                pass
            _record_error(path_str, type(exc).__name__, exc)
            continue

    conn.commit()
    update_state(None, "done")
    conn.commit()

    _log(logger, "Marcando duplicatas por sha256+md5...")
    dup_cur = conn.execute(
        "SELECT sha256 FROM files WHERE sha256 IS NOT NULL GROUP BY sha256 HAVING COUNT(*) > 1"
    )
    dup_count = 0
    for idx, (sha,) in enumerate(dup_cur, start=1):
        if stop_event and stop_event.is_set():
            _log(logger, "Parada solicitada.")
            break
        seen_md5 = {}
        rows = conn.execute(
            "SELECT path, hash FROM files WHERE sha256=? ORDER BY path",
            (sha,),
        ).fetchall()
        for path_str, md5 in rows:
            if not md5:
                continue
            original = seen_md5.get(md5)
            if original is None:
                seen_md5[md5] = path_str
                continue
            cur.execute("UPDATE files SET duplicate_of=? WHERE path=?", (original, path_str))
        dup_count += 1
        if idx % 200 == 0:
            conn.commit()

    conn.commit()

    finish_run(
        conn,
        run_id_db,
        success=(error_count == 0 and not stopped),
        details={"updated": updated, "dup_hashes": dup_count, "errors": error_count},
    )
    conn.commit()
    conn.close()

    _log(logger, f"ENTENDER fim atualizados={updated}")
    return {"updated": updated, "dup_hashes": dup_count}
