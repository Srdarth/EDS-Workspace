from __future__ import annotations

import hashlib
import logging
import time
import warnings
import os
import re
import unicodedata
from datetime import datetime, timezone
from pathlib import Path
from collections import Counter

from .db import connect, start_run, finish_run, record_error
from .config import load_config
from .utils import should_exclude, mark_excluded

try:
    from PyPDF2 import PdfReader
    try:
        from PyPDF2.errors import PdfReadWarning
    except Exception:  # pragma: no cover - optional dependency
        PdfReadWarning = None
    logging.getLogger("PyPDF2").setLevel(logging.ERROR)
    logging.getLogger("pypdf").setLevel(logging.ERROR)
except Exception:  # pragma: no cover - optional dependency
    PdfReader = None
    PdfReadWarning = None

try:
    import docx  # python-docx
except Exception:  # pragma: no cover - optional dependency
    docx = None

try:
    from PIL import Image, ExifTags
except Exception:  # pragma: no cover - optional dependency
    Image = None
    ExifTags = None

# Silencia avisos comuns de arquivos corrompidos (recuperacao de HD)
warnings.filterwarnings("ignore", message=".*startxref pointer.*")
warnings.filterwarnings("ignore", message=".*Truncated File Read.*")


MAX_PDF_PAGES = 10
MAX_TEXT_BYTES = 2 * 1024 * 1024
FINGERPRINT_BYTES = 1024 * 1024

STOPWORDS = {
    "para",
    "com",
    "uma",
    "umas",
    "uns",
    "por",
    "que",
    "como",
    "nao",
    "sim",
    "mais",
    "menos",
    "entre",
    "sobre",
    "este",
    "esta",
    "esteja",
    "isso",
    "essa",
    "esse",
    "aqui",
    "ali",
    "entao",
    "porque",
    "quando",
    "onde",
    "todo",
    "toda",
    "todos",
    "todas",
    "voce",
    "voc",
    "seu",
    "sua",
    "seus",
    "suas",
    "comigo",
    "junto",
    "from",
    "with",
    "that",
    "this",
    "these",
    "those",
    "into",
    "such",
    "very",
    "what",
    "when",
    "where",
    "which",
    "your",
    "yours",
    "their",
    "theirs",
    "about",
    "after",
    "before",
    "during",
    "under",
    "over",
}

GENERIC_RE = re.compile(
    r"^(file|f|img|image|photo|scan|doc|document|recup|recover|output|dsc|pict|vid|video|mov|untitled)[-_ ]?\d{3,}$",
    re.IGNORECASE,
)

SIGNATURES = [
    (b"%PDF-", ".pdf"),
    (b"PK\x03\x04", ".zip"),
    (b"\x89PNG\r\n\x1a\n", ".png"),
    (b"\xff\xd8\xff", ".jpg"),
    (b"GIF87a", ".gif"),
    (b"GIF89a", ".gif"),
    (b"BM", ".bmp"),
]


def _log(logger, msg: str):
    if logger:
        logger(msg)
    else:
        print(msg)


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _normalize_text(text: str) -> str:
    text = unicodedata.normalize("NFKD", text)
    text = text.encode("ascii", "ignore").decode("ascii")
    text = text.lower()
    text = re.sub(r"[^a-z0-9]+", " ", text)
    return text.strip()


def _slugify(text: str, max_len: int = 60) -> str:
    text = _normalize_text(text)
    text = re.sub(r"\s+", "_", text)
    text = re.sub(r"_+", "_", text).strip("_")
    return text[:max_len]


def _is_generic_name(name: str) -> bool:
    base = Path(name).stem
    if base.isdigit():
        return True
    return bool(GENERIC_RE.match(base))


def _detect_ext(path: Path) -> str | None:
    try:
        with open(path, "rb") as f:
            header = f.read(16)
    except Exception:
        return None
    for sig, ext in SIGNATURES:
        if header.startswith(sig):
            return ext
    if len(header) >= 8 and header[4:8] == b"ftyp":
        return ".mp4"
    return None


def _fingerprint(path: Path, fallback: str | None = None) -> str:
    if fallback:
        return fallback[:8]
    h = hashlib.sha1()
    try:
        size = path.stat().st_size
        with open(path, "rb") as f:
            h.update(f.read(FINGERPRINT_BYTES))
            if size > FINGERPRINT_BYTES * 2:
                f.seek(max(size - FINGERPRINT_BYTES, 0), os.SEEK_SET)
                h.update(f.read(FINGERPRINT_BYTES))
    except Exception:
        return "unknown"
    return h.hexdigest()[:8]


def _extract_pdf_text(path: Path) -> tuple[str | None, str]:
    if not PdfReader:
        return None, ""
    try:
        with warnings.catch_warnings():
            if PdfReadWarning:
                warnings.simplefilter("ignore", PdfReadWarning)
            warnings.simplefilter("ignore", UserWarning)
            reader = PdfReader(str(path), strict=False)
        title = None
        try:
            meta = reader.metadata or {}
            title = meta.get("/Title") or meta.get("Title")
        except Exception:
            title = None
        parts = []
        for page in reader.pages[:MAX_PDF_PAGES]:
            try:
                parts.append(page.extract_text() or "")
            except Exception:
                continue
        return title, "\n".join(parts)
    except Exception:
        return None, ""


def _extract_docx_text(path: Path) -> tuple[str | None, str]:
    if not docx:
        return None, ""
    try:
        doc = docx.Document(str(path))
    except Exception:
        return None, ""
    title = None
    try:
        title = doc.core_properties.title
    except Exception:
        title = None
    parts = [p.text for p in doc.paragraphs if p.text]
    return title, "\n".join(parts[:200])


def _extract_txt_text(path: Path) -> tuple[str | None, str]:
    try:
        with open(path, "rb") as f:
            raw = f.read(MAX_TEXT_BYTES)
        text = raw.decode("utf-8", errors="ignore")
    except Exception:
        return None, ""
    lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
    title = lines[0] if lines else None
    return title, "\n".join(lines[:200])


def _extract_exif_date(path: Path) -> str | None:
    if not Image or not ExifTags:
        return None
    try:
        with Image.open(path) as img:
            exif = img._getexif() or {}
    except Exception:
        return None
    if not exif:
        return None
    tag_map = {v: k for k, v in ExifTags.TAGS.items()}
    key = tag_map.get("DateTimeOriginal") or tag_map.get("DateTime")
    if not key:
        return None
    value = exif.get(key)
    if not value:
        return None
    return str(value)


def _keywords_from_text(text: str, max_terms: int = 6) -> list[str]:
    norm = _normalize_text(text)
    if not norm:
        return []
    tokens = [t for t in norm.split() if len(t) >= 4 and t not in STOPWORDS]
    if not tokens:
        return []
    freq = {}
    for t in tokens:
        freq[t] = freq.get(t, 0) + 1
    ranked = sorted(freq.items(), key=lambda kv: (-kv[1], kv[0]))
    return [w for w, _ in ranked[:max_terms]]


def identify_files(
    db_path: Path,
    identify_max_bytes: int,
    text_preview_chars: int,
    min_confidence: int,
    logger=None,
    progress_cb=None,
    stop_event=None,
    resume_scan: bool = False,
    limit: int | None = None,
    timebox: int | None = None,
):
    conn = connect(db_path)
    cur = conn.cursor()
    run_id_db, _run_key = start_run(
        conn,
        "identify",
        config_snapshot={
            "identify_max_bytes": identify_max_bytes,
            "text_preview_chars": text_preview_chars,
            "min_confidence": min_confidence,
        },
    )
    conn.commit()

    # Regra D: excludes globais e retroativos (idempotente)
    try:
        cfg = load_config()
        excludes = list(cfg.get("exclude_contains") or [])
        mark_excluded(conn, excludes)
    except Exception:
        excludes = []

    cols = {c[1] for c in cur.execute("PRAGMA table_info(files)").fetchall()}
    where_parts = ["path IS NOT NULL"]
    if "status" in cols:
        where_parts.append("status IN ('NEW','new','moved','MOVED')")
    else:
        where_parts.append("1=1")
    if "kind" in cols:
        where_parts.append("(kind IS NULL OR kind='')")
    where_parts.append(
        "("
        "original_name IS NULL OR original_name='' "
        "OR detected_ext IS NULL OR detected_ext='' "
        "OR canonical_name IS NULL OR canonical_name='' "
        "OR name_source IS NULL OR name_source='' "
        "OR name_source IN ('unknown','original')"
        ")"
    )
    where = "WHERE " + " AND ".join(where_parts)
    run_id = str(run_id_db)
    now = _utc_now()
    state_key = "__identify__"
    last_id = 0
    if resume_scan:
        row = cur.execute(
            "SELECT last_path, status FROM scan_state WHERE target=?", (state_key,)
        ).fetchone()
        if row and row[1] == "running" and row[0]:
            try:
                last_id = int(row[0])
                _log(logger, f"Retomar identificar do id>{last_id}")
            except Exception:
                last_id = 0

    def update_state(last: int | None, status: str):
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
            (state_key, str(last) if last is not None else None, run_id, now, status),
        )

    update_state(last_id or None, "running")
    conn.commit()

    total = None
    try:
        total = cur.execute(
            f"SELECT COUNT(*) FROM files {where}" + (" AND id > ?" if last_id else ""),
            (last_id,) if last_id else (),
        ).fetchone()[0]
    except Exception:
        total = None
    _log(logger, f"IDENTIFICAR pendentes={total if total is not None else 'n/a'}")

    updated = 0
    error_count = 0
    skipped_protected = 0
    skipped_permission = 0
    excluded_count = 0
    error_types = Counter()
    error_log_path = None
    error_log_file = None
    error_log_failed = False

    def close_error_log():
        nonlocal error_log_file
        if error_log_file:
            try:
                error_log_file.close()
            except Exception:
                pass
            error_log_file = None

    def _record_error(path_str: str, exc: Exception):
        nonlocal error_count, error_log_path, error_log_file, error_log_failed
        error_count += 1
        err_type = type(exc).__name__
        error_types[err_type] += 1
        if error_count <= 20:
            _log(logger, f"Erro ao identificar: {path_str} -> {err_type}: {exc}")
        try:
            record_error(
                conn,
                run_id=run_id_db,
                stage="identify",
                file_path=path_str,
                error_type=err_type,
                error_msg=str(exc),
            )
        except Exception:
            pass
        if error_log_failed:
            return
        if error_log_file is None:
            try:
                log_dir = Path(db_path).parent / "eddy_logs"
                log_dir.mkdir(parents=True, exist_ok=True)
                error_log_path = log_dir / f"identify_errors_{run_id}.log"
                error_log_file = open(error_log_path, "a", encoding="utf-8")
            except Exception:
                error_log_failed = True
                return
        try:
            error_log_file.write(f"{path_str}\t{err_type}\t{exc}\n")
            error_log_file.flush()
        except Exception:
            error_log_failed = True

    query = (
        "SELECT id, path, ext, extension, hash, size, status, original_name, canonical_name, name_source, duplicate_of, content_id "
        f"FROM files {where}"
    )
    params = []
    if last_id:
        query += " AND id > ?"
        params.append(last_id)
    query += " ORDER BY id"
    read_cur = conn.cursor()
    read_cur.execute(query, params)

    stopped = False
    limit_reached = False
    timebox_hit = False
    processed = 0
    started_ts = time.time()
    last_log = started_ts - 2.0
    batch_size = 1000
    commit_every = 500
    max_per_run = limit if limit is not None else int(cfg.get("identify_max_per_run", 50000) or 50000)
    timebox_s = timebox if timebox is not None else int(cfg.get("identify_timebox", 600) or 600)
    if timebox_s <= 0:
        timebox_s = None
    last_seen_id = last_id
    write_ops = 0
    slow_hint_logged = False

    # primeiro heartbeat em até 2s
    limit_total = min(total, max_per_run) if total is not None else max_per_run
    _log(
        logger,
        f"Identify: done=0/{limit_total} rate=0.0/s skip_perm=0 excluded=0 updated=0 errs=0",
    )

    while True:
        rows = read_cur.fetchmany(batch_size)
        if not rows:
            break
        for (
            fid,
            path_str,
            ext,
            extension,
            hval,
            size,
            status,
            orig_name,
            canon_name,
            name_source,
            duplicate_of,
            content_id,
        ) in rows:
            if processed >= max_per_run:
                _log(
                    logger,
                    f"IDENTIFICAR atingiu limite da rodada: {processed}/{max_per_run}",
                )
                limit_reached = True
                break
            if stop_event and stop_event.is_set():
                _log(logger, "Parada solicitada.")
                stopped = True
                break
            if timebox_s is not None and (time.time() - started_ts) >= timebox_s:
                _log(logger, f"IDENTIFICAR timebox atingido: {timebox_s}s")
                limit_reached = True
                timebox_hit = True
                break

            processed += 1
            last_seen_id = fid

            if status == "excluded":
                continue
            if should_exclude(path_str, excludes):
                try:
                    cur.execute("UPDATE files SET status='excluded' WHERE id=?", (fid,))
                    excluded_count += 1
                    write_ops += 1
                except Exception:
                    pass
                continue

            if progress_cb and (processed == 1 or processed % 300 == 0 or (total is not None and processed == total)):
                progress_cb(processed, total or 0, "identify")

            now = time.time()
            if (now - last_log >= 1.0) or (processed % 5000 == 0):
                rate = processed / max(now - started_ts, 0.001)
                limit_total = min(total, max_per_run) if total is not None else max_per_run
                remaining = max(limit_total - processed, 0)
                _log(
                    logger,
                    f"Identify: done={processed}/{limit_total} rate={rate:.1f}/s "
                    f"skip_perm={skipped_permission} excluded={excluded_count} "
                    f"updated={updated} errs={error_count}",
                )
                if not slow_hint_logged and (now - started_ts) >= 10 and rate < 1.0:
                    _log(logger, "DICA: rate baixo — I/O pesado/antivirus ou commit excessivo.")
                    slow_hint_logged = True
                last_log = now

            p_lower = (path_str or "").lower()
            if r"\$recycle.bin\\" in p_lower or r"\system volume information\\" in p_lower:
                skipped_protected += 1
                try:
                    cur.execute("UPDATE files SET status='excluded' WHERE id=?", (fid,))
                    excluded_count += 1
                    write_ops += 1
                except Exception:
                    pass
                continue

            try:
                path = Path(path_str)
                if not path.exists() or not path.is_file():
                    continue

                if duplicate_of:
                    row = cur.execute(
                        """
                        SELECT canonical_name, detected_ext, name_source, name_confidence, title, keywords, text_preview, content_date
                        FROM files
                        WHERE path=?
                        """,
                        (duplicate_of,),
                    ).fetchone()
                    if row and any(row):
                        (dup_canon, dup_ext, dup_source, dup_conf, dup_title, dup_keywords, dup_preview, dup_date) = row
                        cur.execute(
                            """
                            UPDATE files
                            SET canonical_name=?, detected_ext=?, name_source=?, name_confidence=?,
                                title=?, keywords=?, text_preview=?, content_date=?, status=?
                            WHERE id=?
                            """,
                            (
                                dup_canon,
                                dup_ext,
                                dup_source,
                                dup_conf,
                                dup_title,
                                dup_keywords,
                                dup_preview,
                                dup_date,
                                "identified",
                                fid,
                            ),
                        )
                        updated += 1
                        write_ops += 1
                        continue

                if content_id:
                    row = cur.execute(
                        """
                        SELECT canonical_name, detected_ext, name_source, name_confidence, title, keywords, text_preview, content_date
                        FROM files
                        WHERE content_id=? AND canonical_name IS NOT NULL AND canonical_name!=''
                        LIMIT 1
                        """,
                        (content_id,),
                    ).fetchone()
                    if row:
                        (dup_canon, dup_ext, dup_source, dup_conf, dup_title, dup_keywords, dup_preview, dup_date) = row
                        cur.execute(
                            """
                            UPDATE files
                            SET canonical_name=?, detected_ext=?, name_source=?, name_confidence=?,
                                title=?, keywords=?, text_preview=?, content_date=?, status=?
                            WHERE id=?
                            """,
                            (
                                dup_canon,
                                dup_ext,
                                dup_source,
                                dup_conf,
                                dup_title,
                                dup_keywords,
                                dup_preview,
                                dup_date,
                                "identified",
                                fid,
                            ),
                        )
                        updated += 1
                        write_ops += 1
                        continue

                if orig_name is None or orig_name == "":
                    orig_name = path.name

                detected_ext = _detect_ext(path) or ""
                ext_use = ext or extension or detected_ext or path.suffix.lower()

                title = None
                text = ""
                content_date = None

                if identify_max_bytes and size and size > identify_max_bytes:
                    text = ""
                else:
                    if ext_use == ".pdf":
                        title, text = _extract_pdf_text(path)
                    elif ext_use == ".docx":
                        title, text = _extract_docx_text(path)
                    elif ext_use in (".txt", ".md"):
                        title, text = _extract_txt_text(path)

                if not content_date and ext_use in (".jpg", ".jpeg", ".png", ".heic", ".tiff"):
                    content_date = _extract_exif_date(path)

                keywords = _keywords_from_text(text)
                text_preview = _normalize_text(text)[:text_preview_chars] if text else ""

                confidence = 0
                name_src = "unknown"
                base = ""

                if title:
                    base = title
                    confidence += 70
                    name_src = "title"
                elif keywords:
                    base = " ".join(keywords[:3])
                    confidence += 50
                    name_src = "keywords"

                if detected_ext and detected_ext != (ext or extension or ""):
                    confidence += 10

                if not base and not _is_generic_name(orig_name):
                    name_src = "original"

                canonical = canon_name
                if base and confidence >= min_confidence:
                    slug = _slugify(base)
                    if slug:
                        fingerprint = _fingerprint(path, hval)
                        canonical = f"{slug}__{fingerprint}{ext_use}"
                elif not base and _is_generic_name(orig_name):
                    fingerprint = _fingerprint(path, hval)
                    canonical = f"unknown__{fingerprint}{ext_use}"
                    name_src = "unknown"
                    if confidence < 10:
                        confidence = 10

                new_status = status
                if status in (None, "new", "moved", "discovered", "unchanged"):
                    new_status = "identified"

                cur.execute(
                    """
                    UPDATE files
                    SET original_name=?, detected_ext=?, canonical_name=?, name_source=?, name_confidence=?,
                        title=?, keywords=?, text_preview=?, content_date=?, ext=?, extension=?, status=?
                    WHERE id=?
                    """,
                    (
                        orig_name,
                        detected_ext or ext_use,
                        canonical,
                        name_src,
                        confidence,
                        title,
                        ",".join(keywords) if keywords else None,
                        text_preview,
                        content_date,
                        ext_use,
                        ext_use,
                        new_status,
                        fid,
                    ),
                )
                updated += 1
                write_ops += 1
            except PermissionError:
                skipped_permission += 1
                try:
                    cur.execute("UPDATE files SET status='skip_perm' WHERE id=?", (fid,))
                    write_ops += 1
                except Exception:
                    pass
                continue
            except Exception as exc:
                try:
                    cur.execute("UPDATE files SET status='corrupt' WHERE id=?", (fid,))
                    write_ops += 1
                except Exception:
                    pass
                _record_error(path_str, exc)
                continue

            if write_ops >= commit_every:
                update_state(fid, "running")
                conn.commit()
                write_ops = 0

        if stopped or limit_reached:
            break

    if stopped or limit_reached:
        update_state(last_seen_id or last_id, "running")
    else:
        update_state(None, "done")
    conn.commit()

    finish_run(
        conn,
        run_id_db,
        success=(error_count == 0 and not stopped and not limit_reached),
        details={
            "updated": updated,
            "errors": error_count,
            "processed": processed,
            "limit_reached": limit_reached,
            "timebox_hit": timebox_hit,
        },
    )
    conn.commit()
    conn.close()

    if skipped_protected or skipped_permission:
        _log(logger, f"Pulados: protected={skipped_protected} permission={skipped_permission}")
    if error_count:
        _log(logger, f"Erros: total={error_count} top={error_types.most_common(5)}")
        if error_log_path:
            _log(logger, f"Detalhes de erro: {error_log_path}")
    close_error_log()

    _log(logger, f"IDENTIFICAR fim atualizados={updated}")
    return {"updated": updated}
