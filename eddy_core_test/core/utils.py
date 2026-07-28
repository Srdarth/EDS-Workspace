from __future__ import annotations

from datetime import datetime, timezone
import os


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def safe_filename(name: str) -> str:
    bad = '<>:"/\\|?*'
    for c in bad:
        name = name.replace(c, "_")
    name = name.strip()
    return name or "sem_nome"


def normalize_path(p: str) -> str:
    # Canonical case-insensitive para Windows
    try:
        s = os.path.normpath(str(p))
    except Exception:
        s = str(p)
    return s.lower()

def _normalize_token(token: str) -> str:
    # Nunca strip() no começo: não quebrar UNC/drive.
    # Remover apenas separador final e normalizar.
    token = (token or "").rstrip("\\/")
    token = os.path.normpath(token).lower()
    # marcador iniciado por "\" (não UNC) vira nome de pasta puro
    if token.startswith("\\") and not token.startswith("\\\\") and ":" not in token:
        token = token.lstrip("\\/")
    return token

def should_exclude(path: str, exclude_contains: list[str]) -> bool:
    if not exclude_contains:
        return False
    path_norm = normalize_path(path)
    for token in exclude_contains:
        if not token:
            continue
        tn = _normalize_token(token)
        if not tn:
            continue

        # absolutos (drive/UNC): prefixo
        if ":" in tn or tn.startswith("\\\\"):
            if path_norm.startswith(tn):
                return True
            continue

        # pasta: contem '\tn\' OU termina em '\tn'
        marker = os.sep + tn + os.sep
        if marker in path_norm or path_norm.endswith(os.sep + tn):
            return True
    return False

def mark_excluded(conn, exclude_contains: list[str]) -> int:
    if not exclude_contains:
        return 0
    clauses = []
    params = []
    for token in exclude_contains:
        if not token:
            continue
        tn = _normalize_token(token)
        if not tn:
            continue

        if ":" in tn or tn.startswith("\\\\"):
            # absolutos/UNC: prefix LIKE tn%
            clauses.append("LOWER(path) LIKE ?")
            params.append(f"{tn}%")
        else:
            # pasta: contem '\tn\' ou finaliza em '\tn'
            val = os.sep + tn
            clauses.append("LOWER(path) LIKE ?")
            params.append(f"%{val}{os.sep}%")
            clauses.append("LOWER(path) LIKE ?")
            params.append(f"%{val}")

    if not clauses:
        return 0

    q = "UPDATE files SET status='excluded' WHERE COALESCE(status,'')!='excluded' AND (" + " OR ".join(clauses) + ")"
    cur = conn.execute(q, params)
    conn.commit()
    try:
        return cur.rowcount
    except Exception:
        return 0
