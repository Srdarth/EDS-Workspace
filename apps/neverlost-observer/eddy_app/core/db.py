from __future__ import annotations

import json
import os
import re
import shutil
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

_SCHEMA_READY: set[str] = set()
_SAFE_NAME = re.compile(r"^[A-Za-z0-9_]+$")


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _qname(name: str) -> str:
    if not _SAFE_NAME.match(name):
        raise ValueError(f"unsafe sqlite identifier: {name!r}")
    return name


def _table_exists(con: sqlite3.Connection, table: str) -> bool:
    table = _qname(table)
    row = con.execute(
        "SELECT 1 FROM sqlite_master WHERE type='table' AND name=?",
        (table,),
    ).fetchone()
    return row is not None


def _table_cols(con: sqlite3.Connection, table: str) -> set[str]:
    table = _qname(table)
    rows = con.execute(f"PRAGMA table_info({table})").fetchall()
    return {r[1] for r in rows}


def _db_identity(con: sqlite3.Connection) -> str:
    try:
        rows = con.execute("PRAGMA database_list").fetchall()
        for _seq, name, path in rows:
            if name == "main":
                return path or f":memory:{id(con)}"
    except Exception:
        pass
    return f":memory:{id(con)}"


def _ensure_columns(con: sqlite3.Connection, table: str, columns: list[tuple[str, str]]) -> None:
    if not _table_exists(con, table):
        return
    existing = _table_cols(con, table)
    for col, coltype in columns:
        if col in existing:
            continue
        con.execute(f"ALTER TABLE {_qname(table)} ADD COLUMN {_qname(col)} {coltype}")


def _json_dumps_or_none(value: Any) -> str | None:
    if value is None:
        return None
    try:
        return json.dumps(value, ensure_ascii=False)
    except TypeError:
        return json.dumps(str(value), ensure_ascii=False)


def _validate_json_string(value: Any, fallback: str = "[]") -> str:
    if value is None:
        return fallback
    if not isinstance(value, str):
        value = str(value)
    if not value.strip():
        return fallback
    try:
        json.loads(value)
        return value
    except Exception:
        return fallback


def _extract_roots(payload: Any) -> Any | None:
    if not isinstance(payload, dict):
        return None
    if "roots" in payload:
        return payload.get("roots")
    if "targets" in payload:
        return payload.get("targets")
    return None


def _wal_paths(db_path: Path) -> tuple[Path, Path]:
    wal_path = Path(str(db_path) + "-wal")
    shm_path = Path(str(db_path) + "-shm")
    return wal_path, shm_path


def prepare_runtime_db(src_db_path: Path, base_runtime_dir: Path) -> Path:
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    runtime_dir = base_runtime_dir / f"run_{ts}"
    runtime_dir.mkdir(parents=True, exist_ok=True)
    runtime_db = runtime_dir / "eddy.db"

    if not src_db_path.exists():
        raise RuntimeError(f"DB source not found: {src_db_path}")

    wal_src, shm_src = _wal_paths(src_db_path)
    if not wal_src.exists() or not shm_src.exists():
        try:
            con = sqlite3.connect(str(src_db_path), timeout=60)
            con.execute("PRAGMA busy_timeout=60000;")
            try:
                con.execute("PRAGMA journal_mode=WAL;")
            except Exception:
                pass
            try:
                con.execute("PRAGMA wal_checkpoint(FULL);")
                con.commit()
            except Exception:
                pass
            con.close()
        except Exception:
            pass

    shutil.copy2(src_db_path, runtime_db)
    wal_src, shm_src = _wal_paths(src_db_path)
    wal_dst, shm_dst = _wal_paths(runtime_db)
    if wal_src.exists():
        shutil.copy2(wal_src, wal_dst)
    if shm_src.exists():
        shutil.copy2(shm_src, shm_dst)
    return runtime_db


def sanitize_excluded_paths(con: sqlite3.Connection) -> int:
    if not _table_exists(con, "files"):
        return 0
    patterns = [
        r"%\\$Recycle.Bin\\%",
        r"%\\System Volume Information\\%",
        r"%\\Windows\\%",
        r"%\\Program Files\\%",
        r"%\\Program Files (x86)\\%",
        r"%\\ProgramData\\%",
        r"%\\Recovery\\%",
        r"%\\PerfLogs\\%",
        r"%\\$WINDOWS.~BT\\%",
    ]
    total = 0
    for pat in patterns:
        try:
            cur = con.execute(
                "UPDATE files SET status='excluded' WHERE path LIKE ? AND (status IS NULL OR status!='excluded')",
                (pat,),
            )
            total += int(cur.rowcount or 0)
        except Exception:
            continue
    return total


def _stat_info(path: Path) -> str:
    if not path.exists():
        return "missing"
    try:
        st = path.stat()
        return f"size={st.st_size} mtime={datetime.fromtimestamp(st.st_mtime).isoformat(timespec='seconds')}"
    except Exception:
        return "exists"


def _format_write_error(
    db_path: Path,
    con: sqlite3.Connection | None,
    phase: str,
    err: Exception,
) -> str:
    db_dir = db_path.parent
    wal_path, shm_path = _wal_paths(db_path)
    wal_exists = wal_path.exists()
    shm_exists = shm_path.exists()
    access_db = os.access(db_path, os.W_OK) if db_path.exists() else False
    access_dir = os.access(db_dir, os.W_OK)
    query_only = None
    journal_mode = None
    locking_mode = None
    if con is not None:
        try:
            query_only = con.execute("PRAGMA query_only;").fetchone()[0]
        except Exception:
            pass
        try:
            journal_mode = con.execute("PRAGMA journal_mode;").fetchone()[0]
        except Exception:
            pass
        try:
            locking_mode = con.execute("PRAGMA locking_mode;").fetchone()[0]
        except Exception:
            pass

    lines = [
        "SQLite write probe failed.",
        f"phase: {phase}",
        f"db_path: {db_path}",
        f"db_dir: {db_dir}",
        f"os.access(db, W_OK): {access_db}",
        f"os.access(dir, W_OK): {access_dir}",
        f"query_only: {query_only}",
        f"journal_mode: {journal_mode}",
        f"locking_mode: {locking_mode}",
        f"wal_exists: {wal_exists} ({_stat_info(wal_path)})",
        f"shm_exists: {shm_exists} ({_stat_info(shm_path)})",
        f"error: {err!r}",
    ]
    if journal_mode == "wal" and (not wal_exists or not shm_exists):
        lines.append("possible_wal_shm_issue: WAL mode requires eddy.db-wal and eddy.db-shm")
    return "\n".join(lines)


def _fs_write_probe(db_path: Path) -> None:
    probe_path = db_path.parent / "._eddy_fs_probe.tmp"
    try:
        with open(probe_path, "w", encoding="utf-8") as f:
            f.write("probe")
        os.remove(probe_path)
    except Exception as exc:
        raise RuntimeError(_format_write_error(db_path, None, "fs_probe", exc)) from exc


def _sqlite_write_probe(con: sqlite3.Connection, db_path: Path) -> None:
    try:
        con.execute("SAVEPOINT eddy_probe")
        con.execute("CREATE TABLE IF NOT EXISTS _eddy_write_probe(x INTEGER)")
        con.execute("DROP TABLE IF EXISTS _eddy_write_probe")
        con.execute("ROLLBACK TO eddy_probe")
        con.execute("RELEASE eddy_probe")
    except Exception as exc:
        try:
            con.execute("ROLLBACK TO eddy_probe")
            con.execute("RELEASE eddy_probe")
        except Exception:
            pass
        raise RuntimeError(_format_write_error(db_path, con, "sqlite_probe", exc)) from exc


def connect(db_path: Path) -> sqlite3.Connection:
    con = sqlite3.connect(str(db_path), timeout=60)
    con.row_factory = sqlite3.Row
    con.execute("PRAGMA busy_timeout=60000;")
    con.execute("PRAGMA foreign_keys=ON;")

    try:
        con.execute("PRAGMA journal_mode=WAL;")
    except Exception:
        pass

    _fs_write_probe(db_path)
    _sqlite_write_probe(con, db_path)
    ensure_schema(con)
    return con


def ensure_schema(con: sqlite3.Connection) -> None:
    db_id = _db_identity(con)
    if db_id in _SCHEMA_READY:
        return

    try:
        con.execute(
            """
            CREATE TABLE IF NOT EXISTS files (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                path TEXT UNIQUE,
                organized_path TEXT,
                size INTEGER,
                mtime_ns INTEGER,
                ext TEXT,
                extension TEXT,
                category TEXT,
                filename TEXT,
                quicksig TEXT,
                status TEXT,
                name TEXT,
                kind TEXT,
                context TEXT,
                hash TEXT,
                sha256 TEXT,
                error TEXT,
                duplicate_of TEXT,
                first_seen TEXT,
                last_seen TEXT,
                first_seen_run TEXT,
                last_seen_run TEXT,
                origin TEXT,
                source TEXT,
                content_id TEXT
            )
            """
        )

        con.execute(
            """
            CREATE TABLE IF NOT EXISTS plans (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                src_path TEXT NOT NULL,
                action TEXT NOT NULL,
                dest_path TEXT,
                reason TEXT,
                status TEXT,
                created_at TEXT
            )
            """
        )

        con.execute(
            """
            CREATE TABLE IF NOT EXISTS runs (
                run_id TEXT PRIMARY KEY,
                started_at TEXT NOT NULL,
                finished_at TEXT,
                roots_json TEXT NOT NULL,
                id INTEGER,
                run_key TEXT,
                stage TEXT,
                status TEXT,
                details_json TEXT,
                ended_at TEXT,
                config_snapshot TEXT
            )
            """
        )

        con.execute(
            """
            CREATE TABLE IF NOT EXISTS actions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                run_id INTEGER,
                action_type TEXT,
                src TEXT,
                dst TEXT,
                status TEXT DEFAULT 'PENDING',
                reason TEXT,
                created_at TEXT,
                finished_at TEXT,
                hash_src TEXT,
                hash_dst TEXT,
                error TEXT,
                file_path TEXT,
                target_path TEXT,
                error_msg TEXT
            )
            """
        )

        con.execute(
            """
            CREATE TABLE IF NOT EXISTS scan_state (
                target TEXT PRIMARY KEY,
                last_path TEXT,
                run_id TEXT,
                updated_at TEXT,
                status TEXT
            )
            """
        )

        con.execute(
            """
            CREATE TABLE IF NOT EXISTS dir_state (
                path TEXT PRIMARY KEY,
                mtime_ns INTEGER,
                entry_count INTEGER,
                run_id TEXT,
                updated_at TEXT
            )
            """
        )

        con.execute(
            """
            CREATE TABLE IF NOT EXISTS source_profiles (
                source_root TEXT PRIMARY KEY,
                policy TEXT,
                preferred_dest_root TEXT,
                last_seen TEXT,
                notes TEXT
            )
            """
        )

        con.execute(
            """
            CREATE TABLE IF NOT EXISTS file_locations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                file_id INTEGER,
                file_path TEXT NOT NULL,
                location_path TEXT NOT NULL,
                location_root TEXT,
                action TEXT,
                created_at TEXT
            )
            """
        )

        con.execute(
            """
            CREATE TABLE IF NOT EXISTS errors (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                run_id INTEGER,
                stage TEXT,
                file_path TEXT,
                error_type TEXT,
                error_msg TEXT,
                created_at TEXT
            )
            """
        )

        _ensure_columns(
            con,
            "files",
            [
                ("original_name", "TEXT"),
                ("detected_ext", "TEXT"),
                ("canonical_name", "TEXT"),
                ("name_source", "TEXT"),
                ("name_confidence", "INTEGER"),
                ("title", "TEXT"),
                ("keywords", "TEXT"),
                ("text_preview", "TEXT"),
                ("content_date", "TEXT"),
            ],
        )

        _ensure_columns(
            con,
            "runs",
            [
                ("run_key", "TEXT"),
                ("stage", "TEXT"),
                ("status", "TEXT"),
                ("details_json", "TEXT"),
                ("ended_at", "TEXT"),
                ("config_snapshot", "TEXT"),
                ("roots_json", "TEXT"),
                ("id", "INTEGER"),
                ("finished_at", "TEXT"),
            ],
        )

        if _table_exists(con, "runs"):
            cols = _table_cols(con, "runs")
            if "roots_json" not in cols:
                con.execute("ALTER TABLE runs ADD COLUMN roots_json TEXT")
            try:
                con.execute(
                    "UPDATE runs SET roots_json='[]' WHERE roots_json IS NULL OR TRIM(roots_json)=''"
                )
            except Exception:
                pass

        for stmt in (
            "CREATE UNIQUE INDEX IF NOT EXISTS ux_files_path ON files(path)",
            "CREATE INDEX IF NOT EXISTS idx_files_status ON files(status)",
            "CREATE INDEX IF NOT EXISTS idx_files_kind ON files(kind)",
            "CREATE INDEX IF NOT EXISTS idx_files_name_source ON files(name_source)",
            "CREATE INDEX IF NOT EXISTS idx_files_status_kind ON files(status, kind)",
            "CREATE INDEX IF NOT EXISTS idx_plans_status ON plans(status)",
            "CREATE INDEX IF NOT EXISTS idx_runs_stage ON runs(stage)",
            "CREATE UNIQUE INDEX IF NOT EXISTS ux_file_locations_path ON file_locations(file_path, location_path)",
        ):
            try:
                con.execute(stmt)
            except Exception:
                pass

        con.commit()
        _SCHEMA_READY.add(db_id)

    except Exception:
        try:
            con.rollback()
        except Exception:
            pass
        raise


def start_run(
    con: sqlite3.Connection,
    stage: str,
    config_snapshot: Any | None = None,
    details: Any | None = None,
    roots: Any | None = None,
) -> tuple[int | str, str]:
    info = con.execute("PRAGMA table_info(runs)").fetchall()
    cols = {r[1] for r in info}

    run_key = f"{stage}_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"
    now = _utc_now()

    roots_value = _extract_roots(config_snapshot)
    if roots_value is None:
        roots_value = _extract_roots(details)
    if roots_value is None and roots is not None:
        roots_value = roots
    if roots_value is None:
        roots_value = []

    roots_json = _validate_json_string(_json_dumps_or_none(roots_value), fallback="[]")

    vals: dict[str, Any] = {}
    if "run_id" in cols:
        vals["run_id"] = run_key
    if "run_key" in cols:
        vals["run_key"] = run_key
    if "stage" in cols:
        vals["stage"] = stage
    if "started_at" in cols:
        vals["started_at"] = now
    if "status" in cols:
        vals["status"] = "RUNNING"
    if "config_snapshot" in cols:
        vals["config_snapshot"] = _json_dumps_or_none(config_snapshot)
    if "details_json" in cols:
        vals["details_json"] = _json_dumps_or_none(details)
    if "roots_json" in cols:
        vals["roots_json"] = roots_json

    if not vals:
        raise RuntimeError("runs table has no insertable columns")

    columns = list(vals.keys())
    placeholders = ", ".join(["?"] * len(columns))
    sql = f"INSERT INTO runs ({', '.join(columns)}) VALUES ({placeholders})"
    cur = con.execute(sql, [vals[c] for c in columns])
    rowid = cur.lastrowid

    if "id" in cols and rowid is not None:
        try:
            con.execute("UPDATE runs SET id = COALESCE(id, ?) WHERE rowid=?", (rowid, rowid))
        except Exception:
            pass

    run_id_val: int | str
    if "id" in cols and rowid is not None:
        try:
            got = con.execute("SELECT id FROM runs WHERE rowid=?", (rowid,)).fetchone()
            if got and got[0] is not None:
                run_id_val = int(got[0])
            else:
                run_id_val = int(rowid)
        except Exception:
            run_id_val = int(rowid)
    else:
        run_id_val = vals.get("run_id") or run_key

    if "roots_json" in cols:
        _ = _validate_json_string(vals.get("roots_json"), fallback="[]")

    return run_id_val, run_key


def finish_run(
    con: sqlite3.Connection,
    run_id: int | str,
    success: bool = True,
    status: str | None = None,
    details: Any | None = None,
) -> None:
    info = con.execute("PRAGMA table_info(runs)").fetchall()
    cols = {r[1] for r in info}

    final_status = status or ("COMPLETED" if success else "FAILED")
    now = _utc_now()
    details_json = _json_dumps_or_none(details)

    set_parts: list[str] = []
    params: list[Any] = []

    if "finished_at" in cols:
        set_parts.append("finished_at=?")
        params.append(now)
    if "ended_at" in cols:
        set_parts.append("ended_at=?")
        params.append(now)
    if "status" in cols:
        set_parts.append("status=?")
        params.append(final_status)
    if "details_json" in cols and details_json is not None:
        set_parts.append("details_json=COALESCE(details_json, ?)")
        params.append(details_json)

    if not set_parts:
        return

    where = "rowid=?"
    if isinstance(run_id, int) and "id" in cols:
        where = "id=?"
    elif isinstance(run_id, str) and "run_id" in cols:
        where = "run_id=?"
    elif isinstance(run_id, str) and "run_key" in cols:
        where = "run_key=?"

    params.append(run_id)
    con.execute(f"UPDATE runs SET {', '.join(set_parts)} WHERE {where}", params)


def record_error(
    con: sqlite3.Connection,
    run_id: int | None,
    stage: str,
    file_path: str,
    error_type: str,
    error_msg: str,
    created_at: str | None = None,
) -> None:
    if not _table_exists(con, "errors"):
        return
    cols = _table_cols(con, "errors")
    ts = created_at or _utc_now()
    if {"run_id", "stage", "file_path", "error_type", "error_msg", "created_at"}.issubset(cols):
        con.execute(
            """
            INSERT INTO errors(run_id,stage,file_path,error_type,error_msg,created_at)
            VALUES (?,?,?,?,?,?)
            """,
            (run_id, stage, file_path, error_type, error_msg[:400], ts),
        )
        return
    if {"run_id", "path", "err", "ts"}.issubset(cols):
        con.execute(
            "INSERT INTO errors(run_id,path,err,ts) VALUES (?,?,?,?)",
            (run_id, file_path, f"{error_type}: {error_msg}"[:400], ts),
        )


def insert_action(
    con: sqlite3.Connection,
    run_id: int,
    src: str,
    dst: str,
    action_type: str,
    status: str,
    reason: str | None = None,
    hash_src: str | None = None,
    hash_dst: str | None = None,
    error: str | None = None,
    created_at: str | None = None,
    finished_at: str | None = None,
) -> int | None:
    if not _table_exists(con, "actions"):
        return None
    cols = _table_cols(con, "actions")
    vals: dict[str, Any] = {}
    if "run_id" in cols:
        vals["run_id"] = run_id
    if "action_type" in cols:
        vals["action_type"] = action_type
    if "src" in cols:
        vals["src"] = src or ""
    if "dst" in cols:
        vals["dst"] = dst or ""
    if "status" in cols:
        vals["status"] = status
    if "reason" in cols:
        vals["reason"] = reason
    if "created_at" in cols:
        vals["created_at"] = created_at or _utc_now()
    if "finished_at" in cols:
        vals["finished_at"] = finished_at
    if "hash_src" in cols:
        vals["hash_src"] = hash_src
    if "hash_dst" in cols:
        vals["hash_dst"] = hash_dst
    if "error" in cols:
        vals["error"] = error
    if "file_path" in cols:
        vals["file_path"] = src or ""
    if "target_path" in cols:
        vals["target_path"] = dst or ""
    if "error_msg" in cols:
        vals["error_msg"] = error

    if not vals:
        return None

    columns = list(vals.keys())
    placeholders = ", ".join(["?"] * len(columns))
    cur = con.execute(
        f"INSERT INTO actions ({', '.join(columns)}) VALUES ({placeholders})",
        [vals[c] for c in columns],
    )
    try:
        return int(cur.lastrowid) if cur.lastrowid is not None else None
    except Exception:
        return None


def update_action(
    con: sqlite3.Connection,
    action_id: int,
    status: str,
    error: str | None = None,
    finished_at: str | None = None,
    hash_dst: str | None = None,
) -> None:
    if not _table_exists(con, "actions"):
        return
    cols = _table_cols(con, "actions")
    set_parts: list[str] = []
    params: list[Any] = []
    if "status" in cols:
        set_parts.append("status=?")
        params.append(status)
    if "error" in cols:
        set_parts.append("error=COALESCE(error, ?)")
        params.append(error)
    if "error_msg" in cols:
        set_parts.append("error_msg=COALESCE(error_msg, ?)")
        params.append(error)
    if "finished_at" in cols:
        set_parts.append("finished_at=?")
        params.append(finished_at or _utc_now())
    if "hash_dst" in cols:
        set_parts.append("hash_dst=COALESCE(hash_dst, ?)")
        params.append(hash_dst)
    if not set_parts:
        return
    params.append(action_id)
    con.execute(f"UPDATE actions SET {', '.join(set_parts)} WHERE id=?", params)
