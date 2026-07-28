from __future__ import annotations

import copy
import json
import os
import string
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[2]
APP_DIR = Path(__file__).resolve().parents[1]

SYSTEM_EXCLUDES = [
    "\\\\$RECYCLE.BIN\\\\",
    "\\\\System Volume Information\\\\",
    "\\\\Windows\\\\",
    "\\\\Windows\\\\System32\\\\",
    "\\\\Program Files\\\\",
    "\\\\Program Files (x86)\\\\",
    "\\\\ProgramData\\\\",
    "\\\\Recovery\\\\",
    "\\\\PerfLogs\\\\",
    "\\\\$WINDOWS.~BT\\\\",
    "\\\\AppData\\\\",
]

DEFAULT_RULES = [
    # =========================
    # PROPRIEDADE VISUAL (PRIORIDADE MÁXIMA)
    # =========================
    {
        "type": "name_contains",
        "keywords": ["isabella", "isbl", "isa_"],
        "dest": "Sistema de Propriedade Visual/Isabella",
    },
    {
        "type": "name_contains",
        "keywords": ["viviane", "vivian"],
        "dest": "Sistema de Propriedade Visual/Viviane",
    },
    {
        "type": "name_contains",
        "keywords": ["catarina"],
        "dest": "Sistema de Propriedade Visual/Catarina",
    },
    {
        "type": "name_contains",
        "keywords": ["mirella"],
        "dest": "Sistema de Propriedade Visual/Mirella",
    },
    {
        "type": "name_contains",
        "keywords": ["sophia"],
        "dest": "Sistema de Propriedade Visual/Sophia",
    },
    {
        "type": "name_contains",
        "keywords": ["yasmin"],
        "dest": "Sistema de Propriedade Visual/Yasmin",
    },
    # =========================
    # CLASSIFICAÇÃO POR EXTENSÃO
    # =========================
    {
        "type": "ext_in",
        "exts": [".jpg", ".jpeg", ".png", ".webp", ".bmp", ".gif", ".heic", ".tiff"],
        "dest": "00_ARQUIVO_GERAL/01_IMAGENS",
    },
    {
        "type": "ext_in",
        "exts": [".mp4", ".mov", ".avi", ".mkv", ".wmv", ".m4v", ".webm"],
        "dest": "00_ARQUIVO_GERAL/02_VIDEOS",
    },
    {
        "type": "ext_in",
        "exts": [".mp3", ".flac", ".wav", ".aac", ".ogg", ".m4a", ".wma"],
        "dest": "00_ARQUIVO_GERAL/04_AUDIO",
    },
    {
        "type": "ext_in",
        "exts": [".zip", ".rar", ".7z", ".gz", ".tar", ".bz2"],
        "dest": "00_ARQUIVO_GERAL/05_COMPACTADOS",
    },
    {
        "type": "ext_in",
        "exts": [".pdf", ".doc", ".docx", ".ppt", ".pptx", ".xls", ".xlsx", ".epub"],
        "dest": "00_ARQUIVO_GERAL/03_DOCUMENTOS",
    },
    # =========================
    # TELEGRAM (REGRA ESPECÍFICA)
    # =========================
    {
        "type": "path_contains",
        "keywords": ["telegram"],
        "dest": "00_ARQUIVO_GERAL/03_DOCUMENTOS",
    },
    # =========================
    # FALLBACK FINAL
    # =========================
    {
        "type": "fallback",
        "dest": "00_ARQUIVO_GERAL/99_OUTROS",
    },
]

DEFAULT_CONFIG = {
    "db_path": str(ROOT_DIR / "eddy.db"),
    "targets": [],
    "auto_targets": True,
    "system_drive_policy": "users_only",
    "exclude_contains": list(SYSTEM_EXCLUDES),
    "dir_cache": True,
    "dest_root": str(ROOT_DIR / "EddY_Organizado"),
    "rules": DEFAULT_RULES,
    "fallback_dest": "_INBOX",
    "quarantine_dir": "_QUARANTINE",
    "hash_max_bytes": 25 * 1024 * 1024,
    "identify_max_bytes": 50 * 1024 * 1024,
    "identify_max_per_run": 50000,
    "identify_timebox": 600,
    "text_preview_chars": 400,
    "name_confidence_min": 60,
    "dry_run": True,
    "precount": False,
    "mark_missing": False,
    "missing_scope": "targets",
    "resume_scan": True,
    "plan_duplicates": False,
    "action_mode": "copy",
    "language": "pt-BR",
    "theme": "light",
}


def detect_targets(system_drive_policy: str | None = None, skip_system_drive: bool = False) -> list[str]:
    if os.name == "nt":
        policy = (system_drive_policy or "users_only").lower()
        sys_drive = os.environ.get("SystemDrive", "C:").rstrip("\\/") + "\\"
        drives = []
        for letter in string.ascii_uppercase:
            path = f"{letter}:\\"
            if os.path.exists(path):
                if os.path.normcase(path) == os.path.normcase(sys_drive):
                    if skip_system_drive:
                        continue
                    if policy == "skip":
                        continue
                    if policy == "users_only":
                        users_path = Path(path) / "Users"
                        if users_path.exists():
                            drives.append(str(users_path))
                            continue
                drives.append(path)
        return drives
    return [str(ROOT_DIR)]


def _load_json(path: Path) -> dict:
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}


def _merge(base: dict, override: dict) -> dict:
    out = copy.deepcopy(base)
    for key, value in override.items():
        out[key] = value
    return out


def load_config() -> dict:
    cfg = copy.deepcopy(DEFAULT_CONFIG)
    explicit_targets = False

    targets_path = ROOT_DIR / "targets.json"
    tdata = _load_json(targets_path)
    if isinstance(tdata, dict):
        if "targets" in tdata:
            cfg["targets"] = tdata.get("targets", [])
            explicit_targets = True
        if "exclude_contains" in tdata:
            cfg["exclude_contains"] = tdata.get("exclude_contains", [])

    app_cfg_path = APP_DIR / "eddy_config.json"
    app_data = _load_json(app_cfg_path)
    if isinstance(app_data, dict) and app_data:
        cfg = _merge(cfg, app_data)
        if "targets" in app_data:
            explicit_targets = True

    if not explicit_targets and (cfg.get("auto_targets") or not cfg.get("targets")):
        skip_system = False
        sys_drive = os.environ.get("SystemDrive", "C:").rstrip("\\/").upper()
        if not explicit_targets and sys_drive == "C:":
            skip_system = True
        cfg["targets"] = detect_targets(cfg.get("system_drive_policy", "users_only"), skip_system_drive=skip_system)

    cfg["targets_explicit"] = explicit_targets

    excludes = list(cfg.get("exclude_contains") or [])
    for token in SYSTEM_EXCLUDES:
        if token not in excludes:
            excludes.append(token)
    # DISABLED: nao injetar dest no exclude
    # root_token = str(ROOT_DIR)
    # dest_token = str(ROOT_DIR / "EddY_Organizado")
    # for token in (root_token, dest_token):
    #     if token not in excludes:
    #         excludes.append(token)
    cfg["exclude_contains"] = excludes
    return cfg


def save_config(cfg: dict) -> Path:
    path = APP_DIR / "eddy_config.json"
    path.write_text(json.dumps(cfg, indent=2), encoding="utf-8")
    return path
