from __future__ import annotations

import hashlib
import os
import time
import sqlite3
from pathlib import Path
from datetime import datetime
from collections import Counter

from .db import connect, start_run, finish_run
from .utils import should_exclude, normalize_path

HASH_PARTIAL_BYTES = 2 * 1024 * 1024


def _log(logger, msg: str):
    if logger:
        logger(msg)
    else:
        print(msg)


def quick_signature(path: Path, size: int) -> str:
    h = hashlib.sha1()
    h.update(str(size).encode("utf-8"))
    try:
        with open(path, "rb") as f:
            chunk = f.read(HASH_PARTIAL_BYTES)
            h.update(chunk)
    except Exception:
        h.update(b"NOACCESS")
    return h.hexdigest()


def _source_root(path: Path) -> str:
    drive = path.drive
    if drive:
        return f"{drive}\\"
    if path.anchor:
        return path.anchor
    return ""


def count_files(paths: list[str], exclude_contains: list[str]) -> int:
    total = 0
    for base in paths:
        basep = Path(base)
        if not basep.exists():
            continue
        for root, dirs, files in os.walk(basep):
            dirs[:] = sorted(dirs)
            files = sorted(files)
            for name in files:
                p = Path(root) / name
                if should_exclude(str(p), exclude_contains):
                    continue
                total += 1
    return total


def observe(
    db_path: Path,
    targets: list[str],
    exclude_contains: list[str],
    logger=None,
    progress_cb=None,
    precount: bool = False,
    mark_missing: bool = True,
    stop_event=None,
    missing_scope: str = "targets",
    resume_scan: bool = False,
    dir_cache: bool = False,
):
    conn = connect(db_path)
    cur = conn.cursor()
    run_id_db, _run_key = start_run(
        conn,
        "observe",
        config_snapshot={"targets": targets, "precount": precount, "mark_missing": mark_missing},
    )
    conn.commit()
    run_id = str(run_id_db)

    total_items = None
    exclude_local = list(exclude_contains or [])
    db_token = str(Path(db_path))
    if db_token and db_token not in exclude_local:
        exclude_local.append(db_token)
    if dir_cache and precount:
        _log(logger, "Dir cache ativo: precount desativado para evitar varredura dupla.")
        precount = False

    if precount:
        _log(logger, "Contando itens para progresso...")
        total_items = count_files(targets, exclude_local)
        if total_items == 0:
            _log(logger, "Nenhum item encontrado nos alvos.")
            finish_run(conn, run_id_db, success=True, details={"total": 0})
            conn.commit()
            conn.close()
            return {"new": 0, "moved": 0, "unchanged": 0, "missing": 0, "errors": 0}

    resume_run_id = None
    if resume_scan:
        norm_targets = {normalize_path(str(Path(t))) for t in targets if Path(t).exists()}
        rows = cur.execute(
            "SELECT target, last_path, run_id, updated_at, status FROM scan_state"
        ).fetchall()

        # Migra chaves antigas (ex: C:\\ vs c:\\) para o formato normalizado
        for target, last_path, run_id, updated_at, status in rows:
            norm = normalize_path(target)
            if norm != target:
                cur.execute(
                    """
                    INSERT INTO scan_state (target, last_path, run_id, updated_at, status)
                    VALUES (?, ?, ?, ?, ?)
                    ON CONFLICT(target) DO UPDATE SET
                      last_path=excluded.last_path,
                      run_id=excluded.run_id,
                      updated_at=excluded.updated_at,
                      status=excluded.status
                    """,
                    (norm, normalize_path(last_path) if last_path else None, run_id, updated_at, status),
                )
                cur.execute("DELETE FROM scan_state WHERE target=?", (target,))
        conn.commit()

        def _is_stale(ts: str | None) -> bool:
            if not ts:
                return False
            try:
                age = datetime.now() - datetime.fromisoformat(ts)
                return age.total_seconds() > 12 * 3600
            except Exception:
                return False

        running = cur.execute(
            "SELECT target, run_id, updated_at FROM scan_state WHERE status='running' AND run_id IS NOT NULL"
        ).fetchall()
        running_active = []
        for target, run_id, updated_at in running:
            if normalize_path(target) not in norm_targets:
                cur.execute(
                    "UPDATE scan_state SET status=? WHERE target=?",
                    ("stale", target),
                )
                continue
            if _is_stale(updated_at):
                cur.execute(
                    "UPDATE scan_state SET status=? WHERE target=?",
                    ("stale", target),
                )
                continue
            running_active.append((target, run_id, updated_at))
        conn.commit()

        if running_active:
            running_active.sort(key=lambda r: r[2] or "", reverse=True)
            resume_run_id = running_active[0][1]
            _log(logger, f"Retomando run anterior: {resume_run_id}")
    id_is_pk = False
    next_id = None
    try:
        info = conn.execute("PRAGMA table_info(files)").fetchall()
        id_info = next((r for r in info if r[1] == "id"), None)
        if id_info and id_info[5] == 1:
            id_is_pk = True
        if not id_is_pk:
            nulls = conn.execute("SELECT COUNT(*) FROM files WHERE id IS NULL").fetchone()[0]
            if nulls:
                conn.execute("UPDATE files SET id = rowid WHERE id IS NULL")
                conn.commit()
                _log(logger, f"IDs preenchidos por rowid: {nulls}")
            next_id = conn.execute("SELECT COALESCE(MAX(id), 0) + 1 FROM files").fetchone()[0]
    except Exception:
        id_is_pk = True

    now = datetime.now().isoformat(timespec="seconds")

    new_count = 0
    moved_count = 0
    unchanged_count = 0
    missing_count = 0
    error_count = 0
    error_types = Counter()
    error_log_path = None
    error_log_file = None
    error_log_failed = False
    seen = 0
    skipped_dirs = 0

    def update_state(target: str, last_path: str | None, status: str):
        ts = datetime.now().isoformat(timespec="seconds")
        target_key = normalize_path(target)
        last_norm = normalize_path(last_path) if last_path else None
        cur.execute(
            """
            INSERT INTO scan_state (target, last_path, run_id, updated_at, status)
            VALUES (?, ?, ?, ?, ?)
            ON CONFLICT(target) DO UPDATE SET
              last_path=excluded.last_path,
              run_id=excluded.run_id,
              updated_at=excluded.updated_at,
              status=excluded.status
            """,
            (target_key, last_norm, run_id, ts, status),
        )

    def close_error_log():
        nonlocal error_log_file
        if error_log_file:
            try:
                error_log_file.close()
            except Exception:
                pass
            error_log_file = None

    def record_error(path_str: str, exc: Exception):
        nonlocal error_count, error_log_path, error_log_file, error_log_failed
        error_count += 1
        err_type = type(exc).__name__
        error_types[err_type] += 1
        if error_count <= 20:
            _log(logger, f"Erro ao ler: {path_str} -> {err_type}: {exc}")
        if error_log_failed:
            return
        if error_log_file is None:
            try:
                log_dir = Path(db_path).parent / "eddy_logs"
                log_dir.mkdir(parents=True, exist_ok=True)
                error_log_path = log_dir / f"observe_errors_{run_id}.log"
                error_log_file = open(error_log_path, "a", encoding="utf-8")
            except Exception:
                error_log_failed = True
                return
        try:
            error_log_file.write(f"{path_str}\t{err_type}\t{exc}\n")
            error_log_file.flush()
        except Exception:
            error_log_failed = True

    _log(logger, f"OBSERVE inicio run={run_id}")
    phase_total = 2 if mark_missing else 1
    _log(logger, f"Fase 1/{phase_total}: escaneando alvos")
    scan_start = time.time()
    scan_last_log = scan_start

    for base in targets:
        basep = Path(base)
        if not basep.exists():
            _log(logger, f"Alvo nao encontrado: {base}")
            continue
        origin = str(basep)
        profile_root = _source_root(basep)
        if profile_root:
            cur.execute(
                """
                INSERT INTO source_profiles (source_root, last_seen)
                VALUES (?, ?)
                ON CONFLICT(source_root) DO UPDATE SET
                  last_seen=excluded.last_seen
                """,
                (profile_root, now),
            )

        target_key = normalize_path(str(basep))
        last_path = None
        if resume_scan:
            row = cur.execute(
                "SELECT last_path, status, run_id FROM scan_state WHERE target=?", (target_key,)
            ).fetchone()
            if not row:
                legacy = cur.execute(
                    "SELECT last_path, status, run_id FROM scan_state WHERE target=?", (str(basep),)
                ).fetchone()
                if legacy:
                    update_state(str(basep), legacy[0], legacy[1] or "running")
                    conn.commit()
                    row = cur.execute(
                        "SELECT last_path, status, run_id FROM scan_state WHERE target=?", (target_key,)
                    ).fetchone()
            if row:
                last_path_row, status_row, run_row = row
                if resume_run_id and run_row == resume_run_id and status_row == "done":
                    _log(logger, f"Alvo ja concluido no run {resume_run_id}: {basep}")
                    continue
                if status_row == "running" and last_path_row:
                    if resume_run_id is None or run_row == resume_run_id:
                        last_path = last_path_row
                        _log(logger, f"Retomar scan: {basep} de {last_path}")

        update_state(str(basep), last_path, "running")
        conn.commit()

        last_path_norm = normalize_path(last_path) if last_path else None
        skip = bool(last_path_norm)
        last_processed = None

        for root, dirs, files in os.walk(basep):
            if stop_event and stop_event.is_set():
                if last_processed:
                    update_state(str(basep), last_processed, "running")
                    conn.commit()
                _log(logger, "Parada solicitada.")
                result = {
                    "new": new_count,
                    "moved": moved_count,
                    "unchanged": unchanged_count,
                    "missing": missing_count,
                    "errors": error_count,
                }
                finish_run(conn, run_id_db, success=False, details=result)
                conn.commit()
                close_error_log()
                conn.close()
                return result

            dirs[:] = sorted(dirs)
            files = sorted(files)

            pruned = []
            for d in dirs:
                dpath = str(Path(root) / d)
                if should_exclude(dpath, exclude_local):
                    continue
                pruned.append(d)
            dirs[:] = pruned

            pruned_files = []
            for fname in files:
                fpath = str(Path(root) / fname)
                if should_exclude(fpath, exclude_local):
                    continue
                pruned_files.append(fname)
            files = pruned_files

            if dir_cache:
                try:
                    root_stat = os.stat(root)
                    dir_mtime_ns = getattr(root_stat, "st_mtime_ns", int(root_stat.st_mtime * 1_000_000_000))
                    entry_count = len(dirs) + len(files)
                    root_norm = normalize_path(root)
                    row = cur.execute(
                        "SELECT mtime_ns, entry_count FROM dir_state WHERE path=?", (root_norm,)
                    ).fetchone()
                    if row and row[0] == dir_mtime_ns and row[1] == entry_count:
                        cur.execute(
                            """
                            INSERT INTO dir_state (path, mtime_ns, entry_count, run_id, updated_at)
                            VALUES (?, ?, ?, ?, ?)
                            ON CONFLICT(path) DO UPDATE SET
                              mtime_ns=excluded.mtime_ns,
                              entry_count=excluded.entry_count,
                              run_id=excluded.run_id,
                              updated_at=excluded.updated_at
                            """,
                            (root_norm, dir_mtime_ns, entry_count, run_id, now),
                        )
                        skipped_dirs += 1
                        if skipped_dirs <= 5:
                            _log(logger, f"Dir cache: pulando {root}")
                        continue
                except Exception:
                    pass

            for fname in files:
                if stop_event and stop_event.is_set():
                    if last_processed:
                        update_state(str(basep), last_processed, "running")
                        conn.commit()
                    _log(logger, "Parada solicitada.")
                    result = {
                        "new": new_count,
                        "moved": moved_count,
                        "unchanged": unchanged_count,
                        "missing": missing_count,
                        "errors": error_count,
                    }
                    finish_run(conn, run_id_db, success=False, details=result)
                    conn.commit()
                    close_error_log()
                    conn.close()
                    return result

                p = Path(root) / fname
                path_str = str(p)

                path_norm = normalize_path(path_str)
                if skip and last_path_norm and path_norm <= last_path_norm:
                    seen += 1
                    if progress_cb and (seen == 1 or seen % 200 == 0):
                        progress_cb(seen, total_items, "observe")
                    if time.time() - scan_last_log >= 5:
                        elapsed = max(time.time() - scan_start, 1.0)
                        rate = seen / elapsed
                        if total_items:
                            remain = max(total_items - seen, 0)
                            eta = remain / max(rate, 0.1)
                            _log(logger, f"Scan: {seen}/{total_items} ({rate:.0f}/s) ETA~{eta:.0f}s")
                        else:
                            _log(logger, f"Scan: {seen} ({rate:.0f}/s)")
                        scan_last_log = time.time()
                    continue
                if skip:
                    skip = False
                    _log(logger, f"Retomado em: {path_str}")

                seen += 1
                if progress_cb and (seen == 1 or seen % 200 == 0):
                    progress_cb(seen, total_items, "observe")
                if time.time() - scan_last_log >= 5:
                    elapsed = max(time.time() - scan_start, 1.0)
                    rate = seen / elapsed
                    if total_items:
                        remain = max(total_items - seen, 0)
                        eta = remain / max(rate, 0.1)
                        _log(logger, f"Scan: {seen}/{total_items} ({rate:.0f}/s) ETA~{eta:.0f}s")
                    else:
                        _log(logger, f"Scan: {seen} ({rate:.0f}/s)")
                    scan_last_log = time.time()

                try:
                    stat = p.stat()
                    size = stat.st_size
                    try:
                        mtime_ns = stat.st_mtime_ns
                    except AttributeError:
                        mtime_ns = int(stat.st_mtime * 1_000_000_000)
                    _SQLITE_INT_MAX = (1 << 63) - 1
                    if mtime_ns > _SQLITE_INT_MAX or mtime_ns < -(1 << 63):
                        mtime_ns = min(max(mtime_ns, -(1 << 63)), _SQLITE_INT_MAX)
                    ext = p.suffix.lower()
                    category = "sem_categoria"
                    sig = quick_signature(p, size)
                    content_id = f"{size}:{sig}"
                    source_root = _source_root(p)

                    cur.execute("SELECT id, quicksig, content_id, status FROM files WHERE path=?", (path_str,))
                    row = cur.fetchone()
                    if row:
                        existing_id, old_sig, old_cid, existing_status = row
                        sticky_statuses = {"identified","understood","planned","excluded","skip_perm","corrupt","verified"}
                        if old_sig and old_sig != sig:
                            status_use = "new"
                        else:
                            status_use = existing_status if (existing_status in sticky_statuses) else "unchanged"
                    else:
                        status_use = "new"

                    if row:
                        cur.execute(
                            """
                            UPDATE files
                            SET size=?, mtime_ns=?, ext=?, extension=?, last_seen=?, last_seen_run=?, quicksig=?, status=?, filename=?, origin=?, source=?, content_id=?
                            WHERE path=?
                            """,
                            (
                                size,
                                mtime_ns,
                                ext,
                                ext,
                                now,
                                run_id,
                                sig,
                                status_use,
                                p.name,
                                origin,
                                source_root,
                                content_id,
                                path_str,
                            ),
                        )
                        unchanged_count += 1
                    else:
                        cur.execute(
                            """
                            SELECT id, path, kind, category, hash, canonical_name, detected_ext, name_source,
                                   name_confidence, title, keywords, text_preview, content_date
                            FROM files
                            WHERE quicksig=? AND size=?
                            LIMIT 1
                            """,
                            (sig, size),
                        )
                        old = cur.fetchone()
                        if old:
                            (
                                old_id,
                                old_path,
                                old_kind,
                                old_category,
                                old_hash,
                                old_canon,
                                old_detected,
                                old_name_source,
                                old_name_conf,
                                old_title,
                                old_keywords,
                                old_preview,
                                old_content_date,
                            ) = old
                            drive_root = Path(old_path).drive
                            drive_ok = True
                            if drive_root:
                                drive_ok = Path(f"{drive_root}\\").exists()
                            if drive_ok and not os.path.exists(old_path):
                                try:
                                    cur.execute(
                                        """
                                        UPDATE files
                                        SET path=?, size=?, mtime_ns=?, ext=?, extension=?, last_seen=?, last_seen_run=?, status=?, filename=?, origin=?, source=?, content_id=?
                                        WHERE id=?
                                        """,
                                        (
                                            path_str,
                                            size,
                                            mtime_ns,
                                            ext,
                                            ext,
                                            now,
                                            run_id,
                                            "moved",
                                            p.name,
                                            origin,
                                            source_root,
                                            content_id,
                                            old_id,
                                        ),
                                    )
                                    moved_count += 1
                                except sqlite3.IntegrityError as exc:
                                    record_error(path_str, exc)
                                    old_path = str(old_path)
                                    fid = None
                                    if not id_is_pk:
                                        fid = next_id
                                        next_id += 1
                                    cur.execute(
                                        """
                                        INSERT INTO files (
                                            id, path, size, mtime_ns, ext, extension, category, status, first_seen, last_seen,
                                            first_seen_run, last_seen_run, quicksig, filename, duplicate_of, origin, source,
                                            kind, hash, canonical_name, detected_ext, name_source, name_confidence, title,
                                            keywords, text_preview, content_date, content_id
                                        )
                                        VALUES (
                                            ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,
                                            ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?
                                        )
                                        ON CONFLICT(path) DO UPDATE SET
                                          size=excluded.size,
                                          mtime_ns=excluded.mtime_ns,
                                          ext=excluded.ext,
                                          extension=excluded.extension,
                                          category=excluded.category,
                                          status=excluded.status,
                                          last_seen=excluded.last_seen,
                                          last_seen_run=excluded.last_seen_run,
                                          quicksig=excluded.quicksig,
                                          filename=excluded.filename,
                                          duplicate_of=excluded.duplicate_of,
                                          origin=excluded.origin,
                                          source=excluded.source,
                                          kind=COALESCE(excluded.kind, files.kind),
                                          hash=COALESCE(excluded.hash, files.hash),
                                          canonical_name=COALESCE(excluded.canonical_name, files.canonical_name),
                                          detected_ext=COALESCE(excluded.detected_ext, files.detected_ext),
                                          name_source=COALESCE(excluded.name_source, files.name_source),
                                          name_confidence=COALESCE(excluded.name_confidence, files.name_confidence),
                                          title=COALESCE(excluded.title, files.title),
                                          keywords=COALESCE(excluded.keywords, files.keywords),
                                          text_preview=COALESCE(excluded.text_preview, files.text_preview),
                                          content_date=COALESCE(excluded.content_date, files.content_date),
                                          content_id=excluded.content_id
                                        """,
                                        (
                                            fid,
                                            path_str,
                                            size,
                                            mtime_ns,
                                            ext,
                                            ext,
                                            category,
                                            "new",
                                            now,
                                            now,
                                            run_id,
                                            run_id,
                                            sig,
                                            p.name,
                                            old_path,
                                            origin,
                                            source_root,
                                            old_kind,
                                            old_hash,
                                            old_canon,
                                            old_detected,
                                            old_name_source,
                                            old_name_conf,
                                            old_title,
                                            old_keywords,
                                            old_preview,
                                            old_content_date,
                                            content_id,
                                        ),
                                    )
                                    new_count += 1
                            else:
                                fid = None
                                if not id_is_pk:
                                    fid = next_id
                                    next_id += 1
                                cur.execute(
                                    """
                                    INSERT INTO files (
                                        id, path, size, mtime_ns, ext, extension, category, status, first_seen, last_seen,
                                        first_seen_run, last_seen_run, quicksig, filename, duplicate_of, origin, source,
                                        kind, hash, canonical_name, detected_ext, name_source, name_confidence, title,
                                        keywords, text_preview, content_date, content_id
                                    )
                                    VALUES (
                                        ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,
                                        ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?
                                    )
                                    ON CONFLICT(path) DO UPDATE SET
                                      size=excluded.size,
                                      mtime_ns=excluded.mtime_ns,
                                      ext=excluded.ext,
                                      extension=excluded.extension,
                                      category=excluded.category,
                                      status=excluded.status,
                                      last_seen=excluded.last_seen,
                                      last_seen_run=excluded.last_seen_run,
                                      quicksig=excluded.quicksig,
                                      filename=excluded.filename,
                                      duplicate_of=excluded.duplicate_of,
                                      origin=excluded.origin,
                                      source=excluded.source,
                                      kind=COALESCE(excluded.kind, files.kind),
                                      hash=COALESCE(excluded.hash, files.hash),
                                      canonical_name=COALESCE(excluded.canonical_name, files.canonical_name),
                                      detected_ext=COALESCE(excluded.detected_ext, files.detected_ext),
                                      name_source=COALESCE(excluded.name_source, files.name_source),
                                      name_confidence=COALESCE(excluded.name_confidence, files.name_confidence),
                                      title=COALESCE(excluded.title, files.title),
                                      keywords=COALESCE(excluded.keywords, files.keywords),
                                      text_preview=COALESCE(excluded.text_preview, files.text_preview),
                                      content_date=COALESCE(excluded.content_date, files.content_date),
                                      content_id=excluded.content_id
                                    """,
                                    (
                                        fid,
                                        path_str,
                                        size,
                                        mtime_ns,
                                        ext,
                                        ext,
                                        category,
                                        "new",
                                        now,
                                        now,
                                        run_id,
                                        run_id,
                                        sig,
                                        p.name,
                                        old_path,
                                        origin,
                                        source_root,
                                        old_kind,
                                        old_hash,
                                        old_canon,
                                        old_detected,
                                        old_name_source,
                                        old_name_conf,
                                        old_title,
                                        old_keywords,
                                        old_preview,
                                        old_content_date,
                                        content_id,
                                    ),
                                )
                                new_count += 1
                        else:
                            fid = None
                            if not id_is_pk:
                                fid = next_id
                                next_id += 1
                            try:
                                cur.execute(
                                    """
                                    INSERT INTO files (
                                        id, path, size, mtime_ns, ext, extension, category, status, first_seen, last_seen,
                                        first_seen_run, last_seen_run, quicksig, filename, origin, source, content_id
                                    )
                                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                                    ON CONFLICT(path) DO UPDATE SET
                                      size=excluded.size,
                                      mtime_ns=excluded.mtime_ns,
                                      ext=excluded.ext,
                                      extension=excluded.extension,
                                      category=excluded.category,
                                      status=excluded.status,
                                      last_seen=excluded.last_seen,
                                      last_seen_run=excluded.last_seen_run,
                                      quicksig=excluded.quicksig,
                                      filename=excluded.filename,
                                      origin=excluded.origin,
                                      source=excluded.source,
                                      content_id=excluded.content_id
                                    """,
                                    (
                                        fid,
                                        path_str,
                                        size,
                                        mtime_ns,
                                        ext,
                                        ext,
                                        category,
                                        "new",
                                        now,
                                        now,
                                        run_id,
                                        run_id,
                                        sig,
                                        p.name,
                                        origin,
                                        source_root,
                                        content_id,
                                    ),
                                )
                                new_count += 1
                            except sqlite3.IntegrityError as exc:
                                record_error(path_str, exc)
                                cur.execute(
                                    """
                                    UPDATE files
                                    SET size=?, mtime_ns=?, ext=?, extension=?, last_seen=?, last_seen_run=?, quicksig=?, status=?, filename=?, origin=?, source=?, content_id=?
                                    WHERE path=?
                                    """,
                                    (
                                        size,
                                        mtime_ns,
                                        ext,
                                        ext,
                                        now,
                                        run_id,
                                        sig,
                                        "unchanged",
                                        p.name,
                                        origin,
                                        source_root,
                                        content_id,
                                        path_str,
                                    ),
                                )
                                unchanged_count += 1

                    last_processed = path_str
                    if (new_count + moved_count + unchanged_count) % 200 == 0:
                        update_state(str(basep), last_processed, "running")
                        conn.commit()

                except Exception as exc:
                    record_error(path_str, exc)

        try:
            root_norm = normalize_path(root)
            root_stat = os.stat(root)
            dir_mtime_ns = getattr(root_stat, "st_mtime_ns", int(root_stat.st_mtime * 1_000_000_000))
            entry_count = len(dirs) + len(files)
            cur.execute(
                """
                INSERT INTO dir_state (path, mtime_ns, entry_count, run_id, updated_at)
                VALUES (?, ?, ?, ?, ?)
                ON CONFLICT(path) DO UPDATE SET
                  mtime_ns=excluded.mtime_ns,
                  entry_count=excluded.entry_count,
                  run_id=excluded.run_id,
                  updated_at=excluded.updated_at
                """,
                (root_norm, dir_mtime_ns, entry_count, run_id, now),
            )
        except Exception:
            pass

        update_state(str(basep), last_processed, "done")
        conn.commit()

    if mark_missing:
        _log(logger, f"Fase 2/{phase_total}: checando faltantes")
        scope = (missing_scope or "targets").lower().strip()
        scope_targets = []
        for base in targets:
            basep = Path(base)
            if not basep.exists():
                continue
            scope_targets.append(str(basep))

        def norm_prefix(p: str) -> str:
            p = os.path.normcase(p)
            if not p.endswith(os.sep):
                p += os.sep
            return p

        prefixes = [norm_prefix(p) for p in scope_targets]

        if scope == "targets" and not prefixes:
            _log(logger, "Missing ignorado: sem alvos validos.")
        else:
            def like_escape(text: str) -> str:
                return text.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")

            params = []
            where = ""
            if scope == "targets" and prefixes:
                clauses = []
                for pref in prefixes:
                    clauses.append("path LIKE ? ESCAPE '\\'")
                    params.append(like_escape(pref) + "%")
                where = "WHERE " + " OR ".join(clauses)

            if where:
                total_rows = cur.execute(f"SELECT COUNT(*) FROM files {where}", params).fetchone()[0]
            else:
                total_rows = cur.execute("SELECT COUNT(*) FROM files").fetchone()[0]

            _log(logger, f"Escopo missing={scope} total={total_rows}")

            missing_key = "__missing__:" + scope
            last_id = 0
            if resume_scan:
                cur.execute("SELECT last_path, status FROM scan_state WHERE target=?", (missing_key,))
                row = cur.fetchone()
                if row and row[1] == "running" and row[0]:
                    try:
                        last_id = int(row[0])
                        _log(logger, f"Retomar missing do id>{last_id}")
                    except Exception:
                        last_id = 0

            base_query = "SELECT id, path FROM files"
            if where:
                base_query += f" {where}"
            if last_id:
                base_query += " AND id > ?" if where else " WHERE id > ?"
                params.append(last_id)
            base_query += " ORDER BY id"

            read_cur = conn.execute(base_query, params)
            processed = 0
            last_log = time.time()
            start_time = time.time()
            while True:
                rows = read_cur.fetchmany(5000)
                if not rows:
                    break
                for fid, path_str in rows:
                    processed += 1
                    if stop_event and stop_event.is_set():
                        _log(logger, "Parada solicitada.")
                        update_state(missing_key, str(fid), "running")
                        conn.commit()
                        break
                    if not os.path.exists(path_str):
                        cur.execute("UPDATE files SET status=? WHERE id=?", ("missing", fid))
                        missing_count += 1
                    if progress_cb and (processed % 3000 == 0 or processed == total_rows):
                        progress_cb(processed, total_rows, "missing")
                    if processed % 3000 == 0:
                        update_state(missing_key, str(fid), "running")
                        conn.commit()
                    if time.time() - last_log >= 5:
                        elapsed = max(time.time() - start_time, 1.0)
                        rate = processed / elapsed
                        if total_rows:
                            remain = max(total_rows - processed, 0)
                            eta = remain / max(rate, 0.1)
                            _log(logger, f"Missing: {processed}/{total_rows} ({rate:.0f}/s) ETA~{eta:.0f}s")
                        else:
                            _log(logger, f"Missing: {processed} ({rate:.0f}/s)")
                        last_log = time.time()
                if stop_event and stop_event.is_set():
                    break
            update_state(missing_key, None, "done")
            conn.commit()

    result = {
        "new": new_count,
        "moved": moved_count,
        "unchanged": unchanged_count,
        "missing": missing_count,
        "errors": error_count,
    }
    finish_run(conn, run_id_db, success=(error_count == 0), details=result)
    conn.commit()
    close_error_log()
    conn.close()

    if error_count:
        summary = ", ".join(f"{k}={v}" for k, v in error_types.most_common(5))
        if summary:
            _log(logger, f"Erros por tipo: {summary}")
        if error_log_path:
            _log(logger, f"Detalhes de erro: {error_log_path}")

    if skipped_dirs:
        _log(logger, f"Dir cache: {skipped_dirs} pastas puladas")

    _log(
        logger,
        f"OBSERVE fim new={new_count} moved={moved_count} unchanged={unchanged_count} missing={missing_count} err={error_count}",
    )
    return result
