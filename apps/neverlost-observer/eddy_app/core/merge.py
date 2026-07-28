from __future__ import annotations

import sqlite3
from pathlib import Path


def _log(logger, msg: str):
    if logger:
        logger(msg)
    else:
        print(msg)


def _cols(conn: sqlite3.Connection, table: str) -> list[str]:
    return [r[1] for r in conn.execute(f"PRAGMA table_info({table})").fetchall()]


def merge_dbs(
    target_db: Path,
    source_dbs: list[Path],
    logger=None,
    progress_cb=None,
    stop_event=None,
    batch_size: int = 5000,
):
    with sqlite3.connect(str(target_db)) as conn_t:
        conn_t.execute("PRAGMA journal_mode=WAL;")
        conn_t.execute("PRAGMA synchronous=NORMAL;")

        tcols = _cols(conn_t, "files")
        if not tcols:
            raise RuntimeError("Target DB has no files table.")

        for src in source_dbs:
            if stop_event and stop_event.is_set():
                _log(logger, "Parada solicitada.")
                break

            if src == target_db:
                _log(logger, f"Pular {src} (mesmo alvo)")
                continue

            with sqlite3.connect(str(src)) as conn_s:
                scols = _cols(conn_s, "files")
                if not scols:
                    _log(logger, f"Pular {src} (sem tabela files)")
                    continue

                common = [c for c in tcols if c in scols and c != "id"]
                if not common:
                    _log(logger, f"Pular {src} (sem colunas em comum)")
                    continue

                total = None
                try:
                    total = conn_s.execute("SELECT COUNT(*) FROM files").fetchone()[0]
                except Exception:
                    total = None

                col_sql = ", ".join(common)
                placeholders = ", ".join("?" * len(common))
                _log(logger, f"Unindo {src} cols={len(common)}")

                cur = conn_s.execute(f"SELECT {col_sql} FROM files")
                conn_t.execute("BEGIN")
                inserted = 0
                seen = 0

                while True:
                    if stop_event and stop_event.is_set():
                        _log(logger, "Parada solicitada.")
                        break
                    rows = cur.fetchmany(batch_size)
                    if not rows:
                        break
                    conn_t.executemany(
                        f"INSERT OR IGNORE INTO files ({col_sql}) VALUES ({placeholders})",
                        rows,
                    )
                    seen += len(rows)
                    inserted += len(rows)
                    if progress_cb and (seen % (batch_size * 2) == 0 or (total and seen >= total)):
                        progress_cb(seen, total, "merge")

                conn_t.commit()
                _log(logger, f"Uniao concluida para {src} linhas={inserted}")
